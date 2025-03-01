import os, time
import json
import torch
import numpy as np
import torch.nn.functional as F
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.utils.data import DataLoader, DistributedSampler
from torch.optim import lr_scheduler
from torch.nn.parallel import DistributedDataParallel as DDP
from model.model import InvISPNet
from dataset.mri_dataset import mriDataset
from config.config import get_arguments
from tensorboardX import SummaryWriter
    
def parse_arguments():
    parser = get_arguments()
    parser.add_argument("--out_path", type=str, default="./results/", help="Path to save checkpoint. ")
    parser.add_argument("--root1", type=str, default="./data/T2", help="Output images. ")
    parser.add_argument("--root2", type=str, default="./data/T1", help="Input images. ")
    parser.add_argument("--root3", type=str, default="./data/PD", help="Another input images. ")
    parser.add_argument("--resume", dest='resume', action='store_true',  help="Resume training. ")
    parser.add_argument("--loss", type=str, default="L2", choices=["L1", "L2"], help="Choose which loss function to use. ")
    parser.add_argument("--lr", type=float, default=0.0001, help="Learning rate")
    parser.add_argument('--local_rank', type=int, default=0)
    args = parser.parse_args()
    return args
    
def init_status(args):
    os.makedirs(args.out_path, exist_ok=True)
    os.makedirs(args.out_path+"%s"%args.task, exist_ok=True)
    os.makedirs(args.out_path+"%s/checkpoint"%args.task, exist_ok=True)
    with open(args.out_path+"%s/commandline_args.yaml"%args.task , 'w') as f:
        json.dump(args.__dict__, f, indent=2)
    
def setup():
    """初始化分布式训练环境"""
    dist.init_process_group("nccl", init_method="env://")  # NCCL 后端（最快）

def cleanup():
    """清理分布式环境"""
    if dist.is_initialized():
        dist.destroy_process_group()

def main(world_size, args):
    # 初始化 DDP
    setup()
    rank = dist.get_rank()
    torch.cuda.set_device(rank % world_size)
    device = torch.device(rank % world_size)
    
    # 载入数据
    dataset = mriDataset(opt=args, root1=args.root1, root2=args.root2, root3=args.root3)
    sampler = DistributedSampler(dataset, shuffle=True)
    dataloader = DataLoader(
        dataset, batch_size=1, num_workers=4, drop_last=True,
        prefetch_factor=2, pin_memory=True, sampler=sampler
    )
    
    # 定义模型
    net = InvISPNet(channel_in=3, channel_out=3, block_num=8).to(device)
    net = DDP(net)

    if args.resume and rank == 0:
        checkpoint_path = f"{args.out_path}/{args.task}/checkpoint/latest.pth"
        net.load_state_dict(torch.load(checkpoint_path, map_location=device))
        print("[INFO] loaded " + args.out_path+"%s/checkpoint/latest.pth"%args.task)
        
    # 优化器和调度器
    optimizer = torch.optim.Adam(net.parameters(), lr=args.lr)
    scheduler = lr_scheduler.MultiStepLR(optimizer, milestones=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200, 250], gamma=0.5)

    # 数据记录
    writer = SummaryWriter(args.out_path+"%s"%args.task)
    
    # 初始化训练
    step = 0
    loss_all = np.zeros((300), dtype='float')
    num_batches = len(dataloader)
    
    print("[INFO] Start to train")

    for epoch in range(0, 300):
        epoch_time = time.time()
        loss_this_time = 0
        dataloader.sampler.set_epoch(epoch)
        for i_batch, sample_batched in enumerate(dataloader):
            step_time = time.time()
            
            input = sample_batched['input_img'].to(device, non_blocking=True)
            target_forward = sample_batched['target_forward_img'].to(device, non_blocking=True)
            input_target = sample_batched['input_target_img'].to(device, non_blocking=True)
            
            # 向前传播
            reconstruct_for = net(input)
            reconstruct_for = torch.clamp(reconstruct_for, 0, 1)
            forward_loss = F.l1_loss(reconstruct_for, target_forward)
            # 反向传播
            reconstruct_rev = net(reconstruct_for, rev=True)
            reconstruct_rev = torch.clamp(reconstruct_rev, 0, 1)
            rev_loss = F.l1_loss(reconstruct_rev, input_target)
            
            writer.add_scalar('forward_loss', forward_loss.item(), global_step=step)
            writer.add_scalar('rev_loss', rev_loss.item(), global_step=step)
            
            loss = args.weight * forward_loss + rev_loss
            writer.add_scalar('loss', loss.item(), global_step=step)
            if rank == 0:
                print('epoch: ' + str(epoch) + ' iter: ' + str(i_batch) +' loss: ' + str(loss.item()))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            loss_this_time = loss_this_time + loss
            step += 1
            
        loss_this_time = loss_this_time / num_batches
        loss_all[epoch] = loss_this_time
        
        torch.save(net.state_dict(), args.out_path+"%s/checkpoint/latest.pth"%args.task)
        if epoch % 1 == 0 and rank == 0:
            # os.makedirs(args.out_path+"%s/checkpoint/%04d"%(args.task,epoch), exist_ok=True)
            torch.save(net.state_dict(), args.out_path+"%s/checkpoint/%04d.pth"%(args.task,epoch))
            print("[INFO] Successfully saved "+args.out_path+"%s/checkpoint/%04d.pth"%(args.task,epoch))
            
        if epoch % 10 == 0 and rank == 0:    
            print("task: %s Epoch: %d Step: %d || loss: %.5f rev_loss: %.10f forward_loss: %.5f  || lr: %f time: %f"%(
                args.task, epoch, step, loss.detach().cpu().numpy(), rev_loss.detach().cpu().numpy(),
                forward_loss.detach().cpu().numpy(), optimizer.param_groups[0]['lr'], time.time()-step_time
            ))

        scheduler.step()   
        
        if rank == 0:
            print("[INFO] Epoch time: ", time.time()-epoch_time, "task: ", args.task)    
    
    if rank == 0:
        print("[INFO] Train finished.")
    cleanup()

if __name__ == '__main__':
    try:
        world_size = torch.cuda.device_count()
        args = parse_arguments()
        torch.set_num_threads(4)
        main(world_size, args)
    finally:
        cleanup()
