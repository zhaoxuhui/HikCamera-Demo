import sys
import threading
import msvcrt
import cv2
import numpy as np
from ctypes import *

# 指定SDK路径，根据自身情况修改
SDK_path = "./Python/MvImport"
sys.path.append(SDK_path)
from MvCameraControl_class import *

# 用于控制退出循环的变量
g_bExit = False


# 将二进制的影像数据转换成numpy的矩阵，方便后处理
def buffer2numpy(data, nWidth, nHeight):
    data_ = np.frombuffer(data, count=int(nWidth * nHeight * 3), dtype=np.uint8, offset=0)
    data_r = data_[0:nWidth * nHeight * 3:3]
    data_g = data_[1:nWidth * nHeight * 3:3]
    data_b = data_[2:nWidth * nHeight * 3:3]

    data_r_arr = data_r.reshape(nHeight, nWidth)
    data_g_arr = data_g.reshape(nHeight, nWidth)
    data_b_arr = data_b.reshape(nHeight, nWidth)
    numArray = np.zeros([nHeight, nWidth, 3], "uint8")

    numArray[:, :, 0] = data_r_arr
    numArray[:, :, 1] = data_g_arr
    numArray[:, :, 2] = data_b_arr
    return numArray


# 定义一个线程，专门用于接收数据流，和主线程分开
def work_thread(cam=0, pData=0, nDataSize=0):
    stOutFrame = MV_FRAME_OUT()
    buf_cache = None
    img_buff = None

    while True:
        # 获取影像缓冲数据
        ret = cam.MV_CC_GetImageBuffer(stOutFrame, 1000)

        if None != stOutFrame.pBufAddr and 0 == ret:
            # 输出影像长、宽等信息
            print("get one frame: Width[%d], Height[%d], nFrameNum[%d]" % (
                stOutFrame.stFrameInfo.nWidth, stOutFrame.stFrameInfo.nHeight, stOutFrame.stFrameInfo.nFrameNum))

            # 将缓冲数据的内存地址赋给buf_cache
            buf_cache = (c_ubyte * stOutFrame.stFrameInfo.nFrameLen)()
            cdll.msvcrt.memcpy(byref(buf_cache), stOutFrame.pBufAddr, stOutFrame.stFrameInfo.nFrameLen)

            n_save_image_size = stOutFrame.stFrameInfo.nWidth * stOutFrame.stFrameInfo.nHeight * 3 + 2048
            if img_buff is None:
                img_buff = (c_ubyte * n_save_image_size)()

            # 转换像素格式为RGB
            stConvertParam = MV_CC_PIXEL_CONVERT_PARAM()
            memset(byref(stConvertParam), 0, sizeof(stConvertParam))
            stConvertParam.nWidth = stOutFrame.stFrameInfo.nWidth
            stConvertParam.nHeight = stOutFrame.stFrameInfo.nHeight
            stConvertParam.pSrcData = cast(buf_cache, POINTER(c_ubyte))
            stConvertParam.nSrcDataLen = stOutFrame.stFrameInfo.nFrameLen
            stConvertParam.enSrcPixelType = stOutFrame.stFrameInfo.enPixelType
            nConvertSize = stOutFrame.stFrameInfo.nWidth * stOutFrame.stFrameInfo.nHeight * 3
            stConvertParam.enDstPixelType = PixelType_Gvsp_RGB8_Packed
            stConvertParam.pDstBuffer = (c_ubyte * nConvertSize)()
            stConvertParam.nDstBufferSize = nConvertSize
            cam.MV_CC_ConvertPixelType(stConvertParam)

            # 将转换后的RGB数据拷贝给img_buff
            cdll.msvcrt.memcpy(byref(img_buff), stConvertParam.pDstBuffer, nConvertSize)

            # 将二进制的img_buff转换为numpy矩阵
            numArray = buffer2numpy(img_buff, stOutFrame.stFrameInfo.nWidth, stOutFrame.stFrameInfo.nHeight)
            numArray_bgr = cv2.cvtColor(numArray, cv2.COLOR_RGB2BGR)
            cv2.imshow("frame", numArray_bgr)
            cv2.waitKey(10)

            # 最后释放缓冲区
            cam.MV_CC_FreeImageBuffer(stOutFrame)
        if g_bExit == True:
            break


if __name__ == "__main__":
    # step1 获取可用设备列表并指定设备类型
    deviceList = MV_CC_DEVICE_INFO_LIST()
    tlayerType = MV_USB_DEVICE
    ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
    # 默认使用第一个可用设备
    print("Find %d devices!" % deviceList.nDeviceNum)
    input("Use the first one as default, press any key to continue/stop ...")

    # step2 创建相机实例并绑定句柄
    cam = MvCamera()
    stDeviceList = cast(deviceList.pDeviceInfo[0], POINTER(MV_CC_DEVICE_INFO)).contents
    ret = cam.MV_CC_CreateHandle(stDeviceList)

    # step3 打开设备
    ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)

    # step4 开始取流
    ret = cam.MV_CC_StartGrabbing()
    try:
        hThreadHandle = threading.Thread(target=work_thread, args=(cam, None, None))
        hThreadHandle.start()
    except:
        print("error: unable to start thread")
    msvcrt.getch()
    g_bExit = True
    hThreadHandle.join()

    # step5 停止取流
    ret = cam.MV_CC_StopGrabbing()
    print("stopped steaming")

    # step6 关闭设备
    ret = cam.MV_CC_CloseDevice()
    print("closed device")

    # step7 销毁句柄
    ret = cam.MV_CC_DestroyHandle()
    print("destroyed handle")
