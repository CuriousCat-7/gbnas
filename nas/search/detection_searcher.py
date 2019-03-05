import logging
import time

from .base_searcher import BaseSearcher
from ..utils import AvgrageMeter
from .utils import acc_func

class DetectionSearcher(BaseSearcher):
  """Search class for classification.
  """

  def __init__(self,
               model,
               gpus,
               train_w_ds,
               train_arch_ds,
               mod_opt_dict,
               arch_opt_dict,
               logger=logging,
               **kwargs):
    """
    Parameters
    ----------
    model : obj::BaseModel
      model for forward and backward
    mod_opt_dict : dict
      model parameter optimizer settings
    arch_opt_dict : dict
      architecture parameter optimizer settings
    gpus : `list` of `int`
      devices used for training
    train_w_ds : dataset
      dataset for training w
    train_arch_ds : dataset
      dataset for traing architecture parameters
    logger : logger
    w_lr_scheduler : `subclass` of _LRScheduler
      default is CosineDecayLR
    w_sche_cfg : dict
      parameters for w_lr_scheduler
    arch_lr_scheduler : 
      default is None
    arch_sche_cfg : dict
      parameters for arch_lr_scheduler
    """
    super(DetectionSearcher, self).__init__(
      model=model, mod_opt_dict=mod_opt_dict,
      arch_opt_dict=arch_opt_dict, gpus=gpus, 
      logger=logger, **kwargs)
    
    # Info
    self._loss_avg = AvgrageMeter('loss')
    self.avgs = []

    # ds
    self.w_ds = train_w_ds
    self.arch_ds = train_arch_ds
  
  def _step_forward(self, img,
                    img_meta,
                    gt_bboxes,
                    gt_bboxes_ignore,
                    gt_labels,
                    gt_masks=None,
                    proposals=None, 
                    mode='w'):
    """Perform one forward step.

    Take inputs, return loss.
    Modify some attributes.
    """
    loss = self.mod(img,
                    img_meta,
                    gt_bboxes,
                    gt_bboxes_ignore,
                    gt_labels,
                    gt_masks=gt_masks,
                    proposals=proposals, 
                    mode=mode)
    self.batch_size = inputs.size()[0]
    


    print(loss)




    self.cur_batch_loss = sum(loss.values())
    return self.cur_batch_loss

  def search(self, **kwargs):
    """Override this method if you need a different
    search procedure.
    """

    num_epoch = kwargs.get('epoch', 100)
    start_w_epoch = kwargs.get('start_w_epoch', 5)
    self.log_frequence = kwargs.get('log_frequence', 50)

    assert start_w_epoch >= 1, "Start to train w first"

    for epoch in range(start_w_epoch):
      self.tic = time.time()
      self.logger.info("Start to train w for epoch %d" % epoch)
      for step, inputs in enumerate(self.w_ds):
        print(inputs)
        input('jsda;')
        self.step_w(**inputs)
        self.batch_end_callback(epoch, step)

    for epoch in range(num_epoch):
      self.tic = time.time()
      self.logger.info("Start to train arch for epoch %d" % (epoch+start_w_epoch))
      for step, inputs in enumerate(self.arch_ds):
        self.step_arch(**inputs)
        self.batch_end_callback(epoch+start_w_epoch, step)
        
      self.tic = time.time()
      self.logger.info("Start to train w for epoch %d" % (epoch+start_w_epoch))
      for step, inputs in enumerate(self.w_ds):
        self.step_w(**inputs)
        self.batch_end_callback(epoch+start_w_epoch, step)  
