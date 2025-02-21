from typing import Dict, Any, List, Optional
from database.crud_manager import CRUDManager
from core.components.browser.browser_manager import BrowserManager
from core.components.action.base_action_handler import BaseActionHandler
import logging
import asyncio

class WorkflowEngine:
    """工作流引擎"""
    
    def __init__(self):
        self.crud_manager = CRUDManager()
        self.browser_manager = BrowserManager()
        self.logger = logging.getLogger(__name__)

    async def execute_workflow(self, workflow_id: int) -> Dict[str, Any]:
        """
        执行工作流
        
        :param workflow_id: 工作流ID
        :return: 执行结果
        """
        try:
            # 加载工作流
            workflow = self.load_workflow(workflow_id)
            if not workflow:
                raise ValueError(f"工作流不存在: {workflow_id}")
            
            # 初始化浏览器
            await self.browser_manager.init()
            
            # 创建上下文和页面
            page = await self.browser_manager.create_page()
            
            # 执行步骤
            results = []
            for step in workflow['steps']:
                try:
                    result = await self._execute_step(page, step)
                    results.append({
                        'step_id': step['id'],
                        'status': 'success',
                        'data': result
                    })
                except Exception as e:
                    self.logger.error(f"步骤执行失败: {e}")
                    results.append({
                        'step_id': step['id'],
                        'status': 'error',
                        'error': str(e)
                    })
                    break
            
            return {
                'workflow_id': workflow_id,
                'status': 'completed',
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"工作流执行失败: {e}")
            return {
                'workflow_id': workflow_id,
                'status': 'error',
                'error': str(e)
            }
        finally:
            await self.browser_manager.close()

    def load_workflow(self, workflow_id: int) -> Optional[Dict[str, Any]]:
        """
        加载工作流
        
        :param workflow_id: 工作流ID
        :return: 工作流数据
        """
        workflow = self.crud_manager.get_workflow(workflow_id)
        if not workflow:
            return None
            
        # 加载步骤
        steps = self.crud_manager.get_workflow_steps(workflow_id)
        workflow['steps'] = sorted(steps, key=lambda x: x['step_order'])
        
        return workflow

    async def _execute_step(self, page: Any, step: Dict[str, Any]) -> Any:
        """
        执行单个步骤
        
        :param page: 页面对象
        :param step: 步骤数据
        :return: 执行结果
        """
        action_type = step['action_type']
        handler = self._get_action_handler(action_type, page)
        
        if not handler:
            raise ValueError(f"不支持的动作类型: {action_type}")
            
        # 验证步骤参数
        if not await handler.validate(step):
            raise ValueError(f"步骤参数验证失败: {step}")
            
        # 执行动作
        return await handler.execute(step)

    def _get_action_handler(self, action_type: str, page: Any) -> Optional[BaseActionHandler]:
        """
        获取动作处理器
        
        :param action_type: 动作类型
        :param page: 页面对象
        :return: 处理器实例
        """
        # TODO: 实现动作处理器的获取逻辑
        return None 