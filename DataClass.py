class ESKF:
    __init__(state, covariance):
        # just a list
        self.state = state
        # mungking numpy
        self.covariance = covariance
