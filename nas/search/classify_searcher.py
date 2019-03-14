import logging
import time

from .base_searcher import BaseSearcher
from ..utils import AvgrageMeter
from .utils import acc_func

class ClassificationSearcher(BaseSearcher):
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
    super(ClassificationSearcher, self).__init__(
      model=model, mod_opt_dict=mod_opt_dict,
      arch_opt_dict=arch_opt_dict, gpus=gpus, 
      logger=logger, **kwargs)
    
    # Info
    self._acc_avg = AvgrageMeter('acc')
    # self._acc_avg.register_func(lambda obj : 
    #         acc_func(getattr(obj, 'cur_batch_output'), 
    #                  getattr(obj, 'cur_batch_target'),
    #                  getattr(obj, 'batch_size')))
    self._ce_avg = AvgrageMeter('ce')
    # self._ce_avg.register_func(lambda obj:
    #         getattr(obj, 'cur_batch_ce'))

    self._loss_avg = AvgrageMeter('loss')
    self.avgs = [self._acc_avg, self._ce_avg]

    # ds
    self.w_ds = train_w_ds
    self.arch_ds = train_arch_ds
  
  def _step_forward(self, inputs, y, mode='w'):
    """Perform one forward step.

    Take inputs, return loss.
    Modify some attributes.
    """
    # TODO(ZhouJ) y is not scatter into specified gpus
    # which makes y and output/loss may sit in different
    # gpus, and that, is very bad
    self.cur_batch_target = y
    if self.decay_temperature:
      tbs_input={'temperature' :  self.temperature}
    else:
      tbs_input = None
    _outputs = self.mod(x=inputs, y=y,
        mode=mode, tbs_input=tbs_input)
    if len(self.gpus) > 1:
      _outputs = map(lambda x: x.mean(), _outputs)
    self.cur_batch_loss, _ce, _acc = _outputs
    self.batch_size = inputs.size()[0]

    self.cur_batch_ce = _ce.detach()
    self.cur_batch_acc = _acc.detach()
    return self.cur_batch_loss
