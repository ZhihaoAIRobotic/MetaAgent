import os 
import ffmpeg
from fsgan.inference.swap import FaceSwapping 
from fsgan.criterions.vgg_loss import VGGLoss
weights_dir = './weights' 
finetune_iterations = 800 
seg_remove_mouth = True 
seg_batch_size = 24 
batch_size = 8 
finetune=True
def encode_audio(video_path, audio_path, output_path): 
    ffmpeg.concat(ffmpeg.input(video_path), ffmpeg.input(audio_path), v=1, a=1).output(output_path, strict='-2').run(overwrite_output=True)

detection_model = os.path.join(weights_dir, 'WIDERFace_DSFD_RES152.pth')
pose_model = os.path.join(weights_dir, 'hopenet_robust_alpha1.pth')
lms_model = os.path.join(weights_dir, 'hr18_wflw_landmarks.pth')
seg_model = os.path.join(weights_dir, 'celeba_unet_256_1_2_segmentation_v2.pth')
reenactment_model = os.path.join(weights_dir, 'nfv_msrunet_256_1_2_reenactment_v2.1.pth')
completion_model = os.path.join(weights_dir, 'ijbc_msrunet_256_1_2_inpainting_v2.pth')
blending_model = os.path.join(weights_dir, 'ijbc_msrunet_256_1_2_blending_v2.pth')
criterion_id_path = os.path.join(weights_dir, 'vggface2_vgg19_256_1_2_id.pth')
criterion_id = VGGLoss(criterion_id_path)


face_swapping = FaceSwapping(
    detection_model=detection_model, pose_model=pose_model, lms_model=lms_model,
    seg_model=seg_model, reenactment_model=reenactment_model,
    completion_model=completion_model, blending_model=blending_model,
    criterion_id=criterion_id,
    finetune=True, finetune_save=True, finetune_iterations=finetune_iterations,
    seg_remove_mouth=finetune_iterations, batch_size=batch_size,
    seg_batch_size=seg_batch_size, encoder_codec='mp4v')

source_path = './docs/examples/conan_obrien.mp4'

select_source = 'longest'

target_path = './docs/examples/shinzo_abe.mp4'

select_target = 'longest'

output_tmp_path = 'output_tmp.mp4'

output_path = 'output.mp4'

face_swapping(source_path, target_path, output_tmp_path,

select_source, select_target, finetune)

# Encode with audio

encode_audio(output_tmp_path, target_path, output_path)