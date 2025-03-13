import pyautogui
import pygetwindow as gw
from PIL import ImageGrab
from pynput import mouse

class ScreenCatcher:
    def __init__(self):
        self.target_window = None   # 存储目标窗口位置信息

    def select_window(self):
        """更改鼠标图标并等待窗口选择"""
        self.target_window = None   # 重置目标窗口
        print("请选择窗口：")
        # 创建鼠标监听器
        with mouse.Listener(on_click=self.on_mouse_click) as listener:
            listener.join()
        
        if self.target_window:
            # 获取窗口截图
            screenshot = self.screen_shot(self.target_window)
            return screenshot
        else:
            print("未选择窗口，或目标窗口无法找到")
            return None

    def on_mouse_click(self, x, y, button, pressed):
        """鼠标点击时选择窗口
        
        参数:
            x, y: 鼠标点击的坐标位置
            button: 被点击的鼠标按钮
            pressed: 鼠标按钮的按下状态

        注意：程序无法处理多显示器的情况，请保证目标窗口和程序在同一个显示器上。
        """
        if pressed:
            if button == mouse.Button.left:
                # 获取所有窗口，包括多个显示器上的窗口
                windows = gw.getAllWindows()
                self.target_window = None
                
                for window in windows:
                    # 判断鼠标点击位置是否在窗口区域内
                    if window.left <= x <= window.left + window.width and window.top <= y <= window.top + window.height:
                        self.target_window = window
                        break
                
                if self.target_window:
                    print("窗口选择完成")
                
                # 停止监听鼠标点击事件
                return False
            elif button == mouse.Button.right:
                # 取消监听并输出“窗口选择取消”
                print("窗口选择取消")
                return False

    def screen_shot(self, window):
        """截取指定窗口的图片
        
        参数:
            window: 要截取的窗口对象
        
        返回:
            截图的PIL Image对象
        """
        if window:
            print("ScreanCatcher: 正在截取窗口区域...")
            # 截取窗口区域
            window_screenshot = ImageGrab.grab(bbox=(window.left, window.top, window.left + window.width, window.top + window.height))
            # window_screenshot.save('window_screenshot.png')
            # print("窗口截图完成")
            return window_screenshot
        else:
            # print("无法截取窗口，窗口对象为空")
            return None

# 示例调用
if __name__ == "__main__":
    app = ScreenCatcher()
    screenshot = app.select_window()
    if screenshot:
        screenshot.show()