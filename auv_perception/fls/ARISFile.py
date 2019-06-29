from __future__ import print_function

import ctypes
import numpy as np

class MasterHeader(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("version", ctypes.c_uint32),
        ("frameCount", ctypes.c_uint32),
        ("frameRate", ctypes.c_uint32),
        ("highResolution", ctypes.c_uint32),
        ("numberOfRawBeams", ctypes.c_uint32),
        ("sampleRate", ctypes.c_float),
        ("samplesPerBeam", ctypes.c_uint32),
        ("receiverGain", ctypes.c_uint32),
        ("windowStart", ctypes.c_float),
        ("windowEnd", ctypes.c_float),
        ("reverse", ctypes.c_uint32),
        ("serialNumber", ctypes.c_uint32),
        ("dateStr", ctypes.c_char * 32),
        ("headerIDStr", ctypes.c_char * 256),
    ]

class FrameHeader(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("frameIndex", ctypes.c_uint32),
        ("frameTime", ctypes.c_uint64),
        ("version", ctypes.c_uint32),
        ("status", ctypes.c_uint32),
        ("sonarTimeStamp", ctypes.c_uint64),
        ("tsDay", ctypes.c_uint32),
        ("tsHour", ctypes.c_uint32),
        ("tsMinute", ctypes.c_uint32),
        ("tsSecond", ctypes.c_uint32),
        ("tsHSecond", ctypes.c_uint32),
        ("transmitMode", ctypes.c_uint32),
        ("windowStart", ctypes.c_float),
        ("windowLength", ctypes.c_float),
        ("threshold", ctypes.c_uint32),
        ("intensity", ctypes.c_int32),
        ("receiverGain", ctypes.c_uint32),
        ("degC1", ctypes.c_uint32),
        ("degC2", ctypes.c_uint32),
        ("humidity", ctypes.c_uint32),
        ("focus", ctypes.c_uint32),
        ("battery", ctypes.c_uint32),
        ("userValue1", ctypes.c_float),
        ("userValue2", ctypes.c_float),
        ("userValue3", ctypes.c_float),
        ("userValue4", ctypes.c_float),
        ("userValue5", ctypes.c_float),
        ("userValue6", ctypes.c_float),
        ("userValue7", ctypes.c_float),
        ("userValue8", ctypes.c_float),
        ("velocity", ctypes.c_float),
        ("depth", ctypes.c_float),
        ("altitude", ctypes.c_float),
        ("pitch", ctypes.c_float),
        ("pitchRate", ctypes.c_float),
        ("roll", ctypes.c_float),
        ("rollRate", ctypes.c_float),
        ("heading", ctypes.c_float),
        ("headingRate", ctypes.c_float),
        ("compassHeading", ctypes.c_float),
        ("compassPitch", ctypes.c_float),
        ("compassRoll", ctypes.c_float),
        ("latitude", ctypes.c_double),
        ("longitude", ctypes.c_double),
        ("sonarPosition", ctypes.c_float),
        ("configFlags", ctypes.c_uint32),
        ("beamTilt", ctypes.c_float),
        ("targetRange", ctypes.c_float),
        ("targetBearing", ctypes.c_float),
        ("targetPresent", ctypes.c_uint32),
        ("firmwareRevision", ctypes.c_uint32),
        ("flags", ctypes.c_uint32),
        ("sourceFrame", ctypes.c_uint32),
        ("waterTemperature", ctypes.c_float),
        ("timerPeriod", ctypes.c_uint32),
        ("sonarX", ctypes.c_float),
        ("sonarY", ctypes.c_float),
        ("sonarZ", ctypes.c_float),
        ("sonarPan", ctypes.c_float),
        ("sonarTilt", ctypes.c_float),
        ("sonarRoll", ctypes.c_float),
        ("panPNNL", ctypes.c_float),
        ("tiltPNNL", ctypes.c_float),
        ("rollPNNL", ctypes.c_float),
        ("vehicleTime", ctypes.c_double),
        ("timeGGK", ctypes.c_float),
        ("dateGGK", ctypes.c_uint32),
        ("qualityGGK", ctypes.c_uint32),
        ("numSatsGGK", ctypes.c_uint32),
        ("dopGGK", ctypes.c_float),
        ("ehtGGK", ctypes.c_float),
        ("heaveTSS", ctypes.c_float),
        ("yearGPS", ctypes.c_uint32),
        ("monthGPS", ctypes.c_uint32),
        ("dayGPS", ctypes.c_uint32),
        ("hourGPS", ctypes.c_uint32),
        ("minuteGPS", ctypes.c_uint32),
        ("secondGPS", ctypes.c_uint32),
        ("hSecondGPS", ctypes.c_uint32),
        ("sonarPanOffset", ctypes.c_float),
        ("sonarTiltOffset", ctypes.c_float),
        ("sonarRollOffset", ctypes.c_float),
        ("sonarXOffset", ctypes.c_float),
        ("sonarYOffset", ctypes.c_float),
        ("sonarZOffset", ctypes.c_float),
        ("transformMatrix", ctypes.c_float * 16),
        ("sampleRate", ctypes.c_float),
        ("accellX", ctypes.c_float),
        ("accellY", ctypes.c_float),
        ("accellZ", ctypes.c_float),
        ("pingMode", ctypes.c_uint32),
        ("frequency", ctypes.c_uint32),
        ("pulseWidth", ctypes.c_uint32),
        ("cyclePeriod", ctypes.c_uint32),
        ("samplePeriod", ctypes.c_uint32),
        ("transmitEnable", ctypes.c_uint32),
        ("frameRate", ctypes.c_float),
        ("soundSpeed", ctypes.c_float),
        ("samplesPerBeam", ctypes.c_uint32),
        ("enable150Volts", ctypes.c_uint32),
        ("sampleStartDelay", ctypes.c_uint32),
        ("largeLens", ctypes.c_uint32),
        ("systemType", ctypes.c_uint32),
        ("sonarSerialNumber", ctypes.c_uint32),
        ("encryptedKey", ctypes.c_uint64),
        ("arisErrorFlags", ctypes.c_uint32),
        ("missedPackets", ctypes.c_uint32),
        ("arisAppVersion", ctypes.c_uint32),
        ("available2", ctypes.c_uint32),
        ("reorderedSamples", ctypes.c_uint32),
        ("salinity", ctypes.c_uint32),
        ("pressure", ctypes.c_float),
        ("batteryVoltage", ctypes.c_float),
        ("mainVoltage", ctypes.c_float),
        ("switchVoltage", ctypes.c_float),
        ("focusMotorMoving", ctypes.c_uint32),
        ("voltageChanging", ctypes.c_uint32),
        ("focusTimeoutFault", ctypes.c_uint32),
        ("focusOverCurrentFault", ctypes.c_uint32),
        ("focusNotFoundFault", ctypes.c_uint32),
        ("focusStalledFault", ctypes.c_uint32),
        ("fpgaTimeoutFault", ctypes.c_uint32),
        ("fpgaBusyFault", ctypes.c_uint32),
        ("fpgaStuckFault", ctypes.c_uint32),
        ("cpuTempFault", ctypes.c_uint32),
        ("psuTempFault", ctypes.c_uint32),
        ("waterTempFault", ctypes.c_uint32),
        ("humidityFault", ctypes.c_uint32),
        ("pressureFault", ctypes.c_uint32),
        ("voltageReadFault", ctypes.c_uint32),
        ("voltageWriteFault", ctypes.c_uint32),
        ("focusCurrentPosition", ctypes.c_uint32),
        ("targetPan", ctypes.c_float),
        ("targetTilt", ctypes.c_float),
        ("targetRoll", ctypes.c_float),
        ("panMotorErrorCode", ctypes.c_uint32),
        ("tillMotorErrorCode", ctypes.c_uint32),
        ("rollMotorErrorCode", ctypes.c_uint32),
        ("panAbsPosition", ctypes.c_float),
        ("tiltAbsPosition", ctypes.c_float),
        ("rollAbsPosition", ctypes.c_float),
        ("panAccellX", ctypes.c_float),
        ("panAccellY", ctypes.c_float),
        ("panAccellZ", ctypes.c_float),
        ("tiltAccellX", ctypes.c_float),
        ("tiltAccellY", ctypes.c_float),
        ("tiltAccellZ", ctypes.c_float),
        ("rollAccellX", ctypes.c_float),
        ("rollAccellY", ctypes.c_float),
        ("rollAccellZ", ctypes.c_float),
        ("appliedSettings", ctypes.c_uint32),
        ("constrainedSettings", ctypes.c_uint32),
        ("invalidSettings", ctypes.c_uint32),
        ("enableInterpacketDelay", ctypes.c_uint32),
        ("interpacketDelayPeriod", ctypes.c_uint32),
        ("uptime", ctypes.c_uint32),
        ("arisAppVersionMajor", ctypes.c_uint16),
        ("arisAppVersionMinor", ctypes.c_uint16),
        ("panVelocity", ctypes.c_float),
        ("tiltVelocity", ctypes.c_float),
        ("rollVelocity", ctypes.c_float),
        ("sentinel", ctypes.c_uint32),
    ]

def beamsForPingMode(pingMode):
    if pingMode in [1, 2]:
        return 48

    if pingMode in [3, 4, 5]:
        return 96

    if pingMode in [6, 7, 8]:
        return 64

    if pingMode in [9, 10, 11, 12]:
        return 128

    return -1


class ARISFrame:
    def __init__(self, header, data):
        self.header = header
        self.data = data

    def width(self):
        return beamsForPingMode(self.header.pingMode)

    def height(self):
        return self.header.samplesPerBeam

    def windowStart(self):
        return self.header.windowStart

    def windowEnd(self):
        return self.windowStart() + self.header.windowLength

    def numpyImage(self):
        return self.data.reshape(self.height(), self.width())

class ARISFrameFile:
    ARIS_VERSION_DDF_05 = 0x05464444

    def __init__(self, fileName):
        self.arisFile = open(fileName, 'rb')

        masterHeaderBytes = self.arisFile.read(1024)
        self.masterHeader = MasterHeader.from_buffer_copy(masterHeaderBytes)
        self.frameByteSize = 1024 + self.masterHeader.numberOfRawBeams * self.masterHeader.samplesPerBeam

        print("ARIS file has {0} frames of size {1}x{2}".format(self.masterHeader.frameCount, self.masterHeader.numberOfRawBeams, self.masterHeader.samplesPerBeam))
        print("Individual frame size is {0} bytes".format(self.frameByteSize))

    def frameOffset(self, frameID):
        return 1024 + frameID * self.frameByteSize

    def frame(self, frameID):

        if frameID < 0 or frameID > self.masterHeader.frameCount:
            raise IndexError("frameID is invalid")

        #Read frame header
        offset = self.frameOffset(frameID)
        self.arisFile.seek(offset)
        frameHeaderBytes = self.arisFile.read(1024)
        frameHeader = FrameHeader.from_buffer_copy(frameHeaderBytes)

        #Small validation of header version
        if frameHeader.version != self.ARIS_VERSION_DDF_05:
            print("Error, header version is invalid. Expected {0} but received {1}.".format(self.ARIS_VERSION_DDF_05, frameHeader.version))
            return None
        #Compute frame data size
        beams = beamsForPingMode(frameHeader.pingMode)

        if beams == -1:
            print("Error, invalid ping mode in header: {0}".format(frameHeader.pingMode))
            return None

        frameByteSize = beams * frameHeader.samplesPerBeam

        #print frameHeader.reorderedSamples

        #Read frame data
        frameBytes = self.arisFile.read(frameByteSize)
        frameBytes = np.fromstring(frameBytes, dtype = np.uint8).reshape(frameHeader.samplesPerBeam, beams)

        return ARISFrame(frameHeader, frameBytes)

    def frameCount(self):
        return self.masterHeader.frameCount

    def frameRate(self):
        return self.masterHeader.frameRate