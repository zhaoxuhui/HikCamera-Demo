import sys
sys.path.append("../MvImport")
from MvCameraControl_class import *
from CamOperation_class import *
import cv2
import numpy as np


def Color_numpy(data,nWidth,nHeight):
    data_ = np.frombuffer(data, count=int(nWidth*nHeight*3), dtype=np.uint8, offset=0)
    data_r = data_[0:nWidth*nHeight*3:3]
    data_g = data_[1:nWidth*nHeight*3:3]
    data_b = data_[2:nWidth*nHeight*3:3]

    data_r_arr = data_r.reshape(nHeight, nWidth)
    data_g_arr = data_g.reshape(nHeight, nWidth)
    data_b_arr = data_b.reshape(nHeight, nWidth)
    numArray = np.zeros([nHeight, nWidth, 3],"uint8")

    numArray[:, :, 0] = data_r_arr
    numArray[:, :, 1] = data_g_arr
    numArray[:, :, 2] = data_b_arr
    return numArray

if __name__ == "__main__":
    # step1 遍历与枚举可用相机
    deviceList = MV_CC_DEVICE_INFO_LIST()
    tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
    ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
    print("Total available cameras:", deviceList.nDeviceNum)

    # step2 创建相机实例并与可用设备绑定
    cam = MvCamera()
    stDeviceList = cast(deviceList.pDeviceInfo[0], POINTER(MV_CC_DEVICE_INFO)).contents
    ret = cam.MV_CC_CreateHandle(stDeviceList)
    print(ret)

    # step3 打开设备并获取数据流
    ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
    ret = cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
    ret = cam.MV_CC_StartGrabbing()
    print(ret)

    # step4 解析数据
    stOutFrame = MV_FRAME_OUT()
    buf_cache = None
    img_buff = None
    ret = cam.MV_CC_GetImageBuffer(stOutFrame, 1000)
    if 0 == ret:
        if None == buf_cache:
            buf_cache = (c_ubyte * stOutFrame.stFrameInfo.nFrameLen)()

        st_frame_info = stOutFrame.stFrameInfo
        cdll.msvcrt.memcpy(byref(buf_cache), stOutFrame.pBufAddr, st_frame_info.nFrameLen)
        n_save_image_size = st_frame_info.nWidth * st_frame_info.nHeight * 3 + 2048
        if img_buff is None:
            img_buff = (c_ubyte * n_save_image_size)()
        
        #转换像素结构体赋值
        stConvertParam = MV_CC_PIXEL_CONVERT_PARAM()
        memset(byref(stConvertParam), 0, sizeof(stConvertParam))
        stConvertParam.nWidth = st_frame_info.nWidth
        stConvertParam.nHeight = st_frame_info.nHeight
        stConvertParam.pSrcData = cast(buf_cache, POINTER(c_ubyte))
        stConvertParam.nSrcDataLen = st_frame_info.nFrameLen
        stConvertParam.enSrcPixelType = st_frame_info.enPixelType

        print(st_frame_info.enPixelType)
        print(PixelType_Gvsp_RGB8_Packed)
        print(PixelType_Gvsp_Mono8)
        print(PixelType_Gvsp_Mono10)
        print(PixelType_Gvsp_Mono12)
        
        # if PixelType_Gvsp_RGB8_Packed == st_frame_info.enPixelType :
        #     numArray = Color_numpy(buf_cache,st_frame_info.nWidth,st_frame_info.nHeight)
        #     mode = "RGB"
        #     print(numArray.shape)

    # # step1 获取可用设备列表
    # deviceList = MV_CC_DEVICE_INFO_LIST()

    # # step2 枚举设备，获取第一个可用设备
    # tlayerType = MV_USB_DEVICE
    # ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)

    # # step3 创建相机实例
    # cam = MvCamera()

    # # step4 选择设备并创建句柄
    # stDeviceList = cast(deviceList.pDeviceInfo[0], POINTER(MV_CC_DEVICE_INFO)).contents
    # ret = cam.MV_CC_CreateHandle(stDeviceList)

    # # step5 打开设备
    # ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)

    # # step5 设置触发模式为off
    # ret = cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)

    # # step6 开始读取数据
    # ret = cam.MV_CC_StartGrabbing()

    # print(ret)

    # stOutFrame = MV_FRAME_OUT()  
    # memset(byref(stOutFrame), 0, sizeof(stOutFrame))
    # data_buf = None

    # ret = cam.MV_CC_GetImageBuffer(stOutFrame, 1000)
    # if None != stOutFrame.pBufAddr and 0 == ret :
    #     if None == data_buf:
    #         data_buf = (c_ubyte * stOutFrame.stFrameInfo.nFrameLen)()
    #     print ("get one frame: Width[%d], Height[%d], nFrameNum[%d]"  % (stOutFrame.stFrameInfo.nWidth, stOutFrame.stFrameInfo.nHeight, stOutFrame.stFrameInfo.nFrameNum))

    #     nRGBSize = stOutFrame.stFrameInfo.nWidth * stOutFrame.stFrameInfo.nHeight * 3
    #     stConvertParam = MV_CC_PIXEL_CONVERT_PARAM()
    #     memset(byref(stConvertParam), 0, sizeof(stConvertParam))
    #     stConvertParam.nWidth = stOutFrame.stFrameInfo.nWidth
    #     stConvertParam.nHeight = stOutFrame.stFrameInfo.nHeight
    #     stConvertParam.pSrcData = data_buf
    #     stConvertParam.nSrcDataLen = stOutFrame.stFrameInfo.nFrameLen
    #     stConvertParam.enSrcPixelType = stOutFrame.stFrameInfo.enPixelType  
    #     stConvertParam.enDstPixelType = PixelType_Gvsp_RGB8_Packed
    #     stConvertParam.pDstBuffer = (c_ubyte * nRGBSize)()
    #     stConvertParam.nDstBufferSize = nRGBSize

    #     ret = cam.MV_CC_ConvertPixelType(stConvertParam)
    #     if ret != 0:
    #         print ("convert pixel fail! ret[0x%x]" % ret)
    #         del data_buf
    #         sys.exit()
        
    #     if data_buf != None:
    #         del data_buf

    #     cam.MV_CC_FreeImageBuffer(stOutFrame)

    #     file_path = "AfterConvert_RGB.raw"   
    #     file_open = open(file_path.encode('ascii'), 'wb+')
    #     try:
    #         img_buff = (c_ubyte * stConvertParam.nDstLen)()
    #         cdll.msvcrt.memcpy(byref(img_buff), stConvertParam.pDstBuffer, stConvertParam.nDstLen)
    #         file_open.write(img_buff)
    #     except:
    #         raise Exception("save file executed failed:%s" % e.message)
    #     finally:
    #         file_open.close() 
    # else:
    #     print ("get one frame fail, ret[0x%x]" % ret)