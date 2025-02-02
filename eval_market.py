"""
Evaluation for market1501.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import flags, app
import os
import torch
import os.path as osp
import numpy as np
import cv2
import pickle
import tqdm
import random
import matplotlib
matplotlib.use('Agg')
from matplotlib.pyplot import imsave

from data.base import pil_loader
from data.data_utils import RandomCrop
from external.hmr.src.util import image as hmr_img_util

curr_path = osp.dirname(osp.abspath(__file__))
cache_path = osp.join(curr_path, 'cachedir')

flags.DEFINE_string('name', 'exp_name', 'Experiment Name')
flags.DEFINE_string('cache_dir', cache_path, 'Cachedir')
# Set it as split in dataloader
flags.DEFINE_integer('gpu_id', 0, 'Which gpu to use')

flags.DEFINE_integer('batch_size', 4, 'Size of minibatches')
flags.DEFINE_integer('num_train_epoch', 0, 'Number of training iterations')

# Flags for logging and snapshotting
flags.DEFINE_string('checkpoint_dir',
                    osp.join(cache_path, 'snapshots'),
                    'Directory where networks are saved')

flags.DEFINE_string('results_dir_base',
                    osp.join(cache_path, 'evaluation'),
                    'Directory where evaluation results will be saved')

flags.DEFINE_string('results_dir', '', 'This gets set automatically now')

flags.DEFINE_integer('max_eval_iter', 0,
                     'Maximum evaluation iterations. 0 => 1 epoch.')

flags.DEFINE_string('img_path', 'data/im1963.jpg', 'Image to run')
flags.DEFINE_integer('img_size', 256, 'image size the network was trained on.')
flags.DEFINE_boolean('hmr', True, 'if true do hmr.')

opts = flags.FLAGS

#add
data_dir = '/auto/k2/adundar/3DSynthesis/data/texformer/datasets/SMPLMarket'


paths_pkl_path = osp.join(data_dir, 'eval_list.pkl')
with open(paths_pkl_path, 'rb') as f:
    img_paths = pickle.load(f)


# smpl dir
smpl_dir = osp.join(data_dir, 'SMPL_RSC', 'pkl')

# smpl part_seg dir
smpl_part_seg_dir = osp.join(data_dir, 'SMPL_RSC', 'parts')
smpl_part_seg_mapping = {3:1, 6:2, 1:3, 2:3, 7:4, 8:4, 4:5, 5:5, 9:6, 10:6, 11:7, 12:7}

# part_seg dir
part_seg_dir = osp.join(data_dir, 'part_seg_EANet')

def preprocess_img(img):
        # input: HxWxC, uint8(0~255)
        img = (img / 255.) * 2 -1
        img = torch.from_numpy(img).float().permute(2, 0, 1)
        return img

def preprocess_seg(seg):
    seg_float = (seg / 7.) * 2 -1
    seg_float = torch.from_numpy(seg_float).float().unsqueeze(0)
    return seg_float

def preprocess_smpl_seg(self, smpl_seg):
    smpl_seg_long = np.zeros(smpl_seg.shape, dtype=int)
    for k in self.smpl_part_seg_mapping.keys():
        smpl_seg_long[smpl_seg==k] = self.smpl_part_seg_mapping[k]
    smpl_seg_long = torch.from_numpy(smpl_seg_long).long().unsqueeze(0)
    return smpl_seg_long

def get_coord(shape):
    y = np.linspace(-1.0, 1.0, num=shape[0])
    x = np.linspace(-1.0, 1.0, num=shape[1])
    coord_y, coord_x = np.meshgrid(y, x, indexing='ij')
    coord = np.concatenate((coord_y[None], coord_x[None]), axis=0)
    return torch.from_numpy(coord).float()

#BURDA BITIYOR

def partition_list(l, partition_size):
    divup = lambda a,b: int((a + b - 1) / b)
    return [l[i*partition_size:(i+1)*partition_size] for i in range(divup(len(l), partition_size))]


def main(_):
    opts.batch_size = 16
    if opts.hmr:
        #from external.hmr.hmr import HMR

        #img_data = pickle.load(open('./cachedir/market1501/data/img_data_market1501.pkl', 'rb'))
        img_data = pickle.load(open('/auto/k2/adundar/3DSynthesis/data/texformer/datasets/SMPLMarket/eval_list.pkl', 'rb'))
        print(img_data)
        #g_id = list(img_data['query'].keys())
        #g_pids = []
        g_camids = []
        img_list = []
        
        return
        for i in range(len(g_id)):
            cam_view = img_data['query'][g_id[i]]
            for cam_id in cam_view.keys():
                img_paths = cam_view[cam_id]
                for img_path_int in img_paths:
                    img_path = "/auto/k2/adundar/3DSynthesis/data/texformer/datasets/SMPLMarket/query" + img_path_int.split('query')[1]
                    #print(img_path)
                    g_pids.append(int(g_id[i]))
                    g_camids.append(int(cam_id))
                    img_list.append((img_path, int(g_id[i])))
        return
        img_batch_list = partition_list(img_list, opts.batch_size)
        print(len(img_list))
        print(len(img_batch_list))
        print(opts.batch_size)
        hmr = HMR(opts.batch_size)
        print('gectim')
        for i in range(len(img_batch_list)-1):
            print(i)
            b = img_batch_list[i]
            img_ori_list = []
            print(len(b))
            for j in range(len(b)):
                print(b[j][0])
                return
                img = cv2.imread(b[j][0])
                img_ori_list.append(np.expand_dims(img, 0))

            img_ori_batch = np.concatenate(img_ori_list, 0)

            theta, img_crop = hmr.predict_batch(img_ori_batch)

            batch = {'theta': theta,
                     'img_crop': img_crop,
                     'img_info': b}

            print(batch['theta'].shape)
            image = batch['img_crop'][0]
            return
            print('dumpliyom')
            with open('/auto/k2/adundar/3DSynthesis/Other_architectures/HPBTT/cachedir/market1501/data/batch_hmr_q/batch_hmr_%d.pkl' % i, 'wb') as f:
                pickle.dump(batch, f)
            print('dumpladim')
    else:
        return
        from .nnutils import predictor_market as pred_util

        predictor = pred_util.MeshPredictor(opts)

        batch_root = '/auto/k2/adundar/3DSynthesis/Other_architectures/HPBTT/cachedir/market1501/data/batch_hmr_q'
        bg_data_path = '/auto/k2/adundar/3DSynthesis/data/texformer/datasets/PRW/PRW-v16.04.20/frames'
        bg_data_list = []

        img_size = (128, 64)
        random_crop = RandomCrop(output_size=img_size)
        img_size_cmr = opts.img_size
        scale_cmr = (float(opts.img_size) / max(img_size))
        center = np.round(np.array(img_size) / 2).astype(int)
        # image center in (x,y)
        center = center[::-1]

        for root, dirs, files in os.walk(bg_data_path):
            for name in tqdm.tqdm(files):
                if name.endswith('.jpg'):
                    bg_data_list.append(os.path.join(root, name))

        random.shuffle(bg_data_list)
        bg_batch_list = partition_list(bg_data_list, opts.batch_size)
        print(len(bg_data_list))
        print(len(bg_batch_list))

        rand_ind = list(range(len(bg_batch_list)-1))
        random.shuffle(rand_ind)

        batch_path = os.listdir(batch_root)
        for i in range(len(batch_path)):
            print(i)
            batch = pickle.load(open(osp.join(batch_root, batch_path[i]), 'rb'))

            bg_img_paths = bg_batch_list[rand_ind[i]]
            bg_img_batch = []
            for p in bg_img_paths:
                bg_img = np.array(pil_loader(p))
                bg_img = random_crop(bg_img)
                if np.random.rand(1) > 0.5:
                    # Need copy bc torch collate doesnt like neg strides
                    bg_img = bg_img[:, ::-1, :]

                bg_img, _ = hmr_img_util.scale_and_crop(bg_img, scale_cmr, center, img_size_cmr)

                # Finally transpose the image to 3xHxW
                bg_img = bg_img / 255.0
                bg_img = np.transpose(bg_img, (2, 0, 1))
                bg_img_batch.append(np.expand_dims(bg_img, 0))

            bg_img_batch = np.concatenate(bg_img_batch, 0)

            # sub_batch_size = 32
            texture_pred_list = []
            mask_pred_list = []
            for k in range(batch['theta'].shape[0]//opts.batch_size):
                sub_batch = {'theta': batch['theta'][k*opts.batch_size:(k+1)*opts.batch_size],
                             'img_crop': batch['img_crop'][k*opts.batch_size:(k+1)*opts.batch_size]}

                outputs = predictor.predict(sub_batch)
                texture_pred_list.append(outputs['texture_pred'].cpu().numpy())
                mask_pred_list.append(outputs['mask_pred'].cpu().numpy())

            texture_pred = np.concatenate(texture_pred_list, 0)
            mask_pred = np.concatenate(mask_pred_list, 0)

            mask_pred_01 = np.expand_dims((mask_pred > 0).astype(np.float), 1)
            texture_pred = texture_pred * mask_pred_01 + bg_img_batch * (1 - mask_pred_01)

            for ii in range(batch['img_crop'].shape[0]):
                img_name = batch['img_info'][ii][0].split('/')[-1]

                if not os.path.exists(opts.img_path):
                    os.mkdir(opts.img_path)

                imsave(osp.join(opts.img_path, img_name),
                       (cv2.resize(texture_pred[ii][:, :, 64:192].transpose(1, 2, 0), (64, 128), interpolation=cv2.INTER_AREA) * 255).astype(np.uint8))

                imsave(osp.join(opts.img_path, img_name.split('.')[0]+'_mask.png'),
                       (cv2.resize(mask_pred_01[ii][:, :, 64:192].repeat(3, 0).transpose(1, 2, 0), (64, 128), interpolation=cv2.INTER_AREA) * 255).astype(np.uint8))


if __name__ == '__main__':
    opts.batch_size = 32
    app.run(main)
