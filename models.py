# models
import os
from tensorflow.keras.layers import Input, Conv2D, Conv3D, ConvLSTM2D, MaxPooling2D, Dropout, concatenate, LeakyReLU,  UpSampling2D, Activation
from tensorflow.keras.models import Model
from tensorflow.keras.regularizers import l2 as L2

def rainnet(look_back, forecast, channels, start_neurons=64, kernel_size=3, model_save=False):
    # This model is for a multiple target
    # 3D
    # input: [look_back, ny, nx, channels]
    # output: [forecast, ny, nx, channels]

    # 2D
    # input: [ny, nx, look_back]
    # output: [ny, nx, forecast]

    """
    RainNet
    The function for building the RainNet (v1.0) model from scratch
    using Keras functional API.

    Parameters:
    input size: tuple(W x H x C), where W (width) and H (height)
    describe spatial dimensions of input data (e.g., 928x928 for RY data);
    and C (channels) describes temporal (depth) dimension of 
    input data (e.g., 4 means accounting four latest radar scans at time
    t-15, t-10, t-5 minutes, and t)
    
    mode: "regression" (default) or "segmentation". 
    For "regression" mode the last activation function is linear, 
    while for "segmentation" it is sigmoid.
    To train RainNet to predict continuous precipitation intensities use 
    "regression" mode. 
    RainNet could be trained to predict the exceedance of specific intensity 
    thresholds. For that purpose, use "segmentation" mode.
    """
    inputs = Input(shape=(None,None,look_back))

    conv1f = Conv2D(start_neurons, kernel_size, padding='same', kernel_initializer='he_normal')(inputs)
    conv1f = Activation("relu")(conv1f)
    conv1s = Conv2D(start_neurons, kernel_size, padding='same', kernel_initializer='he_normal')(conv1f)
    conv1s = Activation("relu")(conv1s)
    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1s)

    conv2f = Conv2D(start_neurons*2, kernel_size, padding='same', kernel_initializer='he_normal')(pool1)
    conv2f = Activation("relu")(conv2f)
    conv2s = Conv2D(start_neurons*2, kernel_size, padding='same', kernel_initializer='he_normal')(conv2f)
    conv2s = Activation("relu")(conv2s)
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2s)

    conv3f = Conv2D(start_neurons*4, kernel_size, padding='same', kernel_initializer='he_normal')(pool2)
    conv3f = Activation("relu")(conv3f)
    conv3s = Conv2D(start_neurons*4, kernel_size, padding='same', kernel_initializer='he_normal')(conv3f)
    conv3s = Activation("relu")(conv3s)
    pool3 = MaxPooling2D(pool_size=(2, 2))(conv3s)

    conv4f = Conv2D(start_neurons*8, kernel_size, padding='same', kernel_initializer='he_normal')(pool3)
    conv4f = Activation("relu")(conv4f)
    conv4s = Conv2D(start_neurons*8, kernel_size, padding='same', kernel_initializer='he_normal')(conv4f)
    conv4s = Activation("relu")(conv4s)
    drop4 = Dropout(0.5)(conv4s)
    pool4 = MaxPooling2D(pool_size=(2, 2))(drop4)

    conv5f = Conv2D(start_neurons*16, kernel_size, padding='same', kernel_initializer='he_normal')(pool4)
    conv5f = Activation("relu")(conv5f)
    conv5s = Conv2D(start_neurons*16, kernel_size, padding='same', kernel_initializer='he_normal')(conv5f)
    conv5s = Activation("relu")(conv5s)
    drop5 = Dropout(0.5)(conv5s)

    up6 = concatenate([UpSampling2D(size=(2, 2))(drop5), conv4s], axis=3)
    conv6 = Conv2D(start_neurons*8, kernel_size, padding='same', kernel_initializer='he_normal')(up6)
    conv6 = Activation("relu")(conv6)
    conv6 = Conv2D(start_neurons*8, kernel_size, padding='same', kernel_initializer='he_normal')(conv6)
    conv6 = Activation("relu")(conv6)

    up7 = concatenate([UpSampling2D(size=(2, 2))(conv6), conv3s], axis=3)
    conv7 = Conv2D(start_neurons*4, kernel_size, padding='same', kernel_initializer='he_normal')(up7)
    conv7 = Activation("relu")(conv7)
    conv7 = Conv2D(start_neurons*4, kernel_size, padding='same', kernel_initializer='he_normal')(conv7)
    conv7 = Activation("relu")(conv7)

    up8 = concatenate([UpSampling2D(size=(2, 2))(conv7), conv2s], axis=3)
    conv8 = Conv2D(start_neurons*2, kernel_size, padding='same', kernel_initializer='he_normal')(up8)
    conv8 = Activation("relu")(conv8)
    conv8 = Conv2D(start_neurons*2, kernel_size, padding='same', kernel_initializer='he_normal')(conv8)
    conv8 = Activation("relu")(conv8)

    up9 = concatenate([UpSampling2D(size=(2, 2))(conv8), conv1s], axis=3)
    conv9 = Conv2D(start_neurons, kernel_size, padding='same', kernel_initializer='he_normal')(up9)
    conv9 = Activation("relu")(conv9)
    conv9 = Conv2D(start_neurons, kernel_size, padding='same', kernel_initializer='he_normal')(conv9)
    conv9 = Activation("relu")(conv9)

    outputs = Conv2D(forecast, 1, activation='linear', kernel_initializer='he_normal')(conv9)
    
    model = Model(inputs=inputs, outputs=outputs)
    return model

def convlstm(look_back, forecast, channels, start_neurons, kernel_size, model_save=False):
	# input: [nt, ny, nx, channels]
	# output: [nt, ny, nx, channels]

    #start_neurons=32
    #with mirrored_strategy.scope():
    inputs = Input(shape=(look_back,None,None,channels))    

    convlstm = ConvLSTM2D(filters=start_neurons, kernel_size=(kernel_size,kernel_size), data_format='channels_last', padding='same', kernel_initializer='he_normal', return_sequences=True, kernel_regularizer=L2(0.01))(inputs)
    convlstm = LeakyReLU(alpha = 0.1)(convlstm)
    convlstm = ConvLSTM2D(filters=start_neurons*2, kernel_size=(kernel_size,kernel_size), data_format='channels_last', padding='same', kernel_initializer='he_normal', return_sequences=True, kernel_regularizer=L2(0.01))(convlstm)
    convlstm = LeakyReLU(alpha = 0.1)(convlstm)
    convlstm = ConvLSTM2D(filters=start_neurons*2, kernel_size=(kernel_size,kernel_size), data_format='channels_last', padding='same', kernel_initializer='he_normal', return_sequences=True, kernel_regularizer=L2(0.01))(convlstm)
    convlstm = LeakyReLU(alpha = 0.1)(convlstm)
    convlstm = ConvLSTM2D(filters=1, kernel_size=(kernel_size,kernel_size), data_format='channels_last', padding='same', kernel_initializer='he_normal', return_sequences=True, kernel_regularizer=L2(0.01))(convlstm)
    convlstm = LeakyReLU(alpha = 0.1)(convlstm)    
    predict = Conv3D(forecast, (3,3,3), activation='linear', padding='same', data_format='channels_first')(convlstm)    
    model = Model(inputs, predict)
    return model
