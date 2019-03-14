



import torch
import torch.nn as nn

class BaseModel(nn.Module):
  """Base class for building neural network.

  You should override forward method to get
  tensors you needed.
  """

  def __init__(self, base,
               tbs_blocks,
               head,
               output_indices=None):
    """
    Parameters
    ----------
    base : 

    tbs_blocks : list

    head : 

    output_indices : list or None
      for fpn

    """
    super(BaseModel, self).__init__()
    self.output_indices = output_indices if output_indices else []

    self.base = base
    if isinstance(tbs_blocks, list):
      self.tbs_blocks = nn.ModuleList(tbs_blocks)
    elif isinstance(tbs_blocks, nn.Module):
      pass
    else:
      raise TypeError("tbs_blocks should be type list or nn.Module")
    self.head = head
    self.arch_params = []
    self.model_params = []
    for b in self.tbs_blocks:
      self.arch_params.append(b.arch_params)
      self.model_params += b.model_params
      # register is not necessary, all blk has registered
      # parameter through self.** = Parameter()
      # self.register_parameter(b.name, b.arch_params)

  def head_loss_(self, output, target):
    return self.head.loss_(output, target)
  
  def speed_test(self, x, base_input=None, 
                 tbs_input=None, head_input=None,
                 device='cuda', verbose=True):
    """Measure speed for tbs blocks.

    TODO(ZhouJ) How to release the memeory taken???
    """
    self.to(device)
    x = x.to(device)
    if verbose:
      print("Doing speed test")
    with torch.autograd.no_grad(): # TODO seems don't work
      self.base.eval()
      if base_input is None:
        x = self.base(x)
      else:
        x = self.base(x, base_input)
      
      for blk in self.tbs_blocks:
        blk.eval()
        x = blk.speed_test(x, device=device, verbose=verbose)
    
  def loss_(self, x, y, mode=None):
    """Calculate loss and return it.

    Under most circumstance, you want to override this.

    TODO(ZhouJ) Sometimes, model parameters and architecture
    parameters use different losses.
    """
    raise NotImplementedError()
