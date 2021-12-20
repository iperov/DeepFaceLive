import torch

class AdaBelief(torch.optim.Optimizer):
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-16,
                 weight_decay=0, lr_dropout = 1.0):

        defaults = dict(lr=lr, lr_dropout=lr_dropout, betas=betas, eps=eps, weight_decay=weight_decay)
        super(AdaBelief, self).__init__(params, defaults)
    
    def reset(self):
        for group in self.param_groups:
            for p in group['params']:
                state = self.state[p]
                state['step'] = 0
                state['m_t'] = torch.zeros_like(p.data,memory_format=torch.preserve_format)
                state['v_t'] = torch.zeros_like(p.data,memory_format=torch.preserve_format)
                
    def set_lr(self, lr):
        for group in self.param_groups:
            group['lr'] = lr

    def step(self):
        for group in self.param_groups:
            for p in group['params']:
                if p.grad is None:
                    continue

                grad = p.grad.data

                beta1, beta2 = group['betas']

                state = self.state[p]
                if len(state) == 0:
                    state['step'] = 0
                    state['m_t'] = torch.zeros_like(p.data,memory_format=torch.preserve_format)
                    state['v_t'] = torch.zeros_like(p.data,memory_format=torch.preserve_format)

                if group['weight_decay'] != 0:
                    grad.add_(p.data, alpha=group['weight_decay'])

                state['step'] += 1

                m_t, v_t = state['m_t'], state['v_t']
                m_t.mul_(beta1).add_( grad            , alpha=1 - beta1)
                v_t.mul_(beta2).add_( (grad - m_t)**2 , alpha=1 - beta2)

                v_diff = (-group['lr'] * m_t).div_( v_t.sqrt().add_(group['eps']) )

                if group['lr_dropout'] < 1.0:
                    lrd_rand = torch.ones_like(p.data)
                    v_diff *= torch.bernoulli(lrd_rand * group['lr_dropout'] )

                p.data.add_(v_diff)
