# -*- coding: utf-8 -*-
from .deploy import deploy as vip_deploy
from .deploy import redeploy as vip_redeploy
from .deploy import undeploy as vip_undeploy

__all__ = ('vip_deploy', 'vip_redeploy', 'vip_undeploy')
