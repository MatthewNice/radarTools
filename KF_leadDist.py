def KF_leadDist(df, plot=False, sd = False):
    """This function is to give a filtered estimation of the state of the lead distance in an offline batch.

    Dataframe input needs only two columns: the measurements of lead distance, and the times of the measurements.
    Make sure that the input values are sorted by time. Columns assumed titled 'Time', and 'Message'.

    Setting plot to True will output plots. SD to True adds in the standard deviationon the plots."""

    from pykalman import KalmanFilter
    import numpy as np
    import matplotlib.pyplot as plt
    import time
    import pandas as pd

    #cleaning up erroneous high lead distance values:
    for i in range(0,len(df.Message)):
        if df.Message[i] > 240:
            df = df.drop(i)

    times = df.Time.values
    measurements = df.Message.values

    initial_state_mean = [measurements[0], #distance
                          0] #relv

    transition_matrix = [[1, 1],
                         [0, 1]]

    observation_matrix = [[1, 0]]

    observation_covariance = [[1]] #R

    transition_covariance = [[1,0],
                            [0,1]] #Q


    kf1 = KalmanFilter(transition_matrices = transition_matrix,
                      observation_matrices = observation_matrix,
                      initial_state_mean = initial_state_mean,
                      transition_covariance =  transition_covariance,
                      observation_covariance = observation_covariance)

    (filtered_state_means, filtered_state_covariances) = kf1.filter(measurements)

    #calculating the variance of the states
    if sd == True:
        D_variance = []
        D_sd=[]
        rV_sd=[]
        for i in range(0,len(filtered_state_covariances)):
            D_variance.append(filtered_state_covariances[i][0][0])
            D_sd.append(3*np.sqrt(filtered_state_covariances[i][0][0]))
            rV_sd.append(1*np.sqrt(filtered_state_covariances[i][1][1]))

        D_1sd_minus = [i * -.33 for i in D_sd]
        D_1sd_plus = [i * .33 for i in D_sd]
        D_sd_minus=  [i * -1 for i in D_sd] #3 st dev minus
        Rv1sd_minus = [i * -1 for i in rV_sd]
    if plot == True:
        plt.figure(1)

        plt.plot(times,measurements,'ro', markersize = 2, label='Measurements')
        plt.plot(times,filtered_state_means[:, 0], 'b--',label='Estimated State')
        if sd == True:
            plt.plot(times,measurements-D_sd, 'g--')
            plt.plot(times,measurements+D_sd, 'g--',label='3SD')
            plt.title('Measurements, Mean State, and Confidence Interval')
        else:
            plt.title('Measurements, and Mean Estimated State')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Lead Distance (meters)')
        plt.legend()
        plt.show()

        slope = pd.Series(np.gradient(df.Message), df.Time, name='CAN RelV')

        plt.figure(2)
        plt.plot(times,filtered_state_means[:, 1], 'b--',label='Estimated Relv State')
        plt.plot(slope,'g--',marker='.',markersize = 5,ls='',label='Gradient from Measurements') #CAN data relv
        plt.title('Relative Velocity State Estimation')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Relative Velocity (meters/second)')
        plt.legend()
        plt.show()

    return filtered_state_means, filtered_state_covariances
