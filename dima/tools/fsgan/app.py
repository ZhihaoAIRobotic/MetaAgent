import os
import ffmpeg
import json
from fsgan.inference.swap import FaceSwapping
from fsgan.criterions.vgg_loss import VGGLoss
from jina import Deployment, Executor, requests
import time
from docarray.documents import TextDoc
from docarray import DocList
import shutil


#config
weights_dir = './weights'

finetune_iterations = 800 
seg_remove_mouth = True 
seg_batch_size = 24
batch_size = 8


def encode_audio(video_path, audio_path, output_path):
  ffmpeg.concat(ffmpeg.input(video_path), ffmpeg.input(audio_path), v=1, a=1) \
    .output(output_path, strict='-2').run(overwrite_output=True)

class fsgan(Executor):
    def __init__(self, **kwargs):
         super().__init__(**kwargs)
         self.detection_model = os.path.join(weights_dir, 'WIDERFace_DSFD_RES152.pth')
         self.pose_model = os.path.join(weights_dir, 'hopenet_robust_alpha1.pth')
         self.lms_model = os.path.join(weights_dir, 'hr18_wflw_landmarks.pth')
         self.seg_model = os.path.join(weights_dir, 'celeba_unet_256_1_2_segmentation_v2.pth')
         self.reenactment_model = os.path.join(weights_dir, 'nfv_msrunet_256_1_2_reenactment_v2.1.pth')
         self.completion_model = os.path.join(weights_dir, 'ijbc_msrunet_256_1_2_inpainting_v2.pth')
         self.blending_model = os.path.join(weights_dir, 'ijbc_msrunet_256_1_2_blending_v2.pth')
         self.criterion_id_path = os.path.join(weights_dir, 'vggface2_vgg19_256_1_2_id.pth')
         self.criterion_id = VGGLoss(self.criterion_id_path)
         self.face_swapping = FaceSwapping(
            detection_model=self.detection_model, pose_model=self.pose_model, lms_model=self.lms_model,
            seg_model=self.seg_model, reenactment_model=self.reenactment_model,
            completion_model=self.completion_model, blending_model=self.blending_model,
            criterion_id=self.criterion_id,
            finetune=True, finetune_save=True, finetune_iterations=finetune_iterations,
            seg_remove_mouth=finetune_iterations, batch_size=batch_size,
            seg_batch_size=seg_batch_size, encoder_codec='mp4v')
    @requests(on='/face_swap')
    def face_swap(self,  docs, **kwargs):
          print('...face_swap...')
          select_source = 'longest'
          select_target = 'longest'
          source_path = docs[0].text 
          target_path = docs[1].text
          output_path = docs[2].text
          finetune = True
          output_tmp_path = 'output_tmp'+'.mp4'  
          # output_path = 'output_'+ '.mp4'
          self.face_swapping(source_path, target_path, output_tmp_path, select_source, select_target, finetune)
          encode_audio(output_tmp_path, target_path, output_path)
          source_path_tmp = source_path[:-4]
          target_path_tmp = target_path[:-4]
          os.remove(output_tmp_path)
          shutil.rmtree(source_path_tmp)
          shutil.rmtree(target_path_tmp)
        
dep = Deployment(uses=fsgan,port=123,protocol='http')


with dep:
    dep.block()





# #load model
# detection_model = os.path.join(weights_dir, 'WIDERFace_DSFD_RES152.pth')
# pose_model = os.path.join(weights_dir, 'hopenet_robust_alpha1.pth')
# lms_model = os.path.join(weights_dir, 'hr18_wflw_landmarks.pth')
# seg_model = os.path.join(weights_dir, 'celeba_unet_256_1_2_segmentation_v2.pth')
# reenactment_model = os.path.join(weights_dir, 'nfv_msrunet_256_1_2_reenactment_v2.1.pth')
# completion_model = os.path.join(weights_dir, 'ijbc_msrunet_256_1_2_inpainting_v2.pth')
# blending_model = os.path.join(weights_dir, 'ijbc_msrunet_256_1_2_blending_v2.pth')
# criterion_id_path = os.path.join(weights_dir, 'vggface2_vgg19_256_1_2_id.pth')
# criterion_id = VGGLoss(criterion_id_path)


# face_swapping = FaceSwapping(
#     detection_model=detection_model, pose_model=pose_model, lms_model=lms_model,
#     seg_model=seg_model, reenactment_model=reenactment_model,
#     completion_model=completion_model, blending_model=blending_model,
#     criterion_id=criterion_id,
#     finetune=True, finetune_save=True, finetune_iterations=finetune_iterations,
#     seg_remove_mouth=finetune_iterations, batch_size=batch_size,
#     seg_batch_size=seg_batch_size, encoder_codec='mp4v')