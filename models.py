
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- Project: LucidNet                                                                                   -- #
# -- Description: A Lightweight Framework for Transparent and Interpretable FeedForward Neural Net       -- #
# -- models.py: python script with Machine Learning Models                                               -- #
# -- Author: IFFranciscoME - if.francisco.me@gmail.com                                                   -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- Repository: https://github.com/IFFranciscoME/LucidNet                                               -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

# import other scripts from the project
import functions as fn

# import libraries for this script
import numpy as np

# ------------------------------------------------------------------------------------------------------ -- #
# ------------------------------------------------------------------- FEEDFORWARD MULTILAYER PERECEPTRON -- #
# ------------------------------------------------------------------------------------------------------ -- #

class Sequential:

    """
    Artificial Neural Network (Feedforward multilayer pereceptron with backpropagation)

    Topology characteristics
    ------------------------

    hidden_l: Number of neurons per hidden layer (list of int, with length of l_hidden)
    hidden_a: Activation of hidden layers (list of str, with length l_hidden)   
    output_n: Number of neurons in output layer (int)
    output_a: Activation of output layer (str)
   
    Other characteristics
    ---------------------

    Layer transformations:
        - linear
        - convolution
   
    Activation functions:
        For hidden -> Sigmoid, Tanh, ReLu
        For output -> Linear (regression), Sigmoid (binary classification), Softmax (multivariate classification)
    
    Methods
    -------
    
    Weights Initialization:
        - Xavier normal, Xavier uniform, common uniform, according to [1]
        - He, according to [2]
        - Load from object.
    
    Training Schemes:
        - Gradient Descent
            - train: use all the data on each epoch
            - validation: use all the data on each epoch
            - note for FTS: None of particular importance

        - Stochastic Gradient Descent
            - train: use 1 example at a time and iterate through all of them on each epoch
            - validation: use all the data when train finishes, do that on each epoch 
            - note for FTS: Do not shuffle data

        - Mini-Batch
            - train: use a partition or subset of the whole data
            - validation: 

        - Nesterov
        - Adam
    
    Regularization:
        - Types: l1, l2, elasticnet, dropout
        
        - In Cost Function:
            - Weights values of all layers (l1, l2, elasticnet)
        
        - In layers
            - Weights gradient values (l1, l2, elasticnet)
            - Bias gradient values (l1, l2, elasticnet)
            - Neurons activation (dropout)

    Cost Functions: 
        - For classification: 
            - Binary Cross-Entropy 
            - Multiclass Cross-Entropy

        - For regression:
            - Mean Squared Error
    
    Execution Tools:
        - Preprocessing input data: Scale, Standard, Robust Standard.
        - Callback for termination on NaN (cost functions divergence).
        - Callback for early stopping on a metric value difference between Train-Validation sets.
        - Save weights to external object/file.
        - Load weights from external object/file.

    Visualization/Interpretation Tools: 
        - Weight values per layer (Colored bar for each neuron, separation of all layers).
        - CostFunction (train-val) evolution (two lines plot with two y-axis).
        - Convolution operation between layers.
    
    Methods
        - __private: init, init_weights, activation, forward, backward, derivative
        - _protected: train, cost, metrics, regularization, callback
        - public: fit, predict, explain, load, save
    
    Special

    "Ubuntu does not mean that people should not address themselves, the question, therefore is, are you
     going to do so in order to enable the community around you?", Nelson Mandela, 2006. Recorded in a 
     video made previously to the launch of Ubuntu linux distribution.

    - ubuntu_fit: Distributed learning using parallel processing among mini-batches of data selected by its 
                  value on an information divergence matrix.

    - ubuntu_predict: Voting system (classification) or Average system (regression).

    """

    # -------------------------------------------------------------------------------- CLASS CONSTRUCTOR -- #
    # -------------------------------------------------------------------------------------------------- -- #

    def __init__(self, hidden_l, hidden_a, output_n, output_a, cost_f=None, cost_r=None,
                 hidden_r=None):

        """
        ANN Class constructor
        
        Parameters
        ----------

        hidden_l: list (of int)
            Number of neurons per hidden layer

        hidden_a: list (list of str, with length hidden_l)
            Activation of hidden layers

        output_n: int
            Number of neurons in output layer

        output_a: str
            Activation of output layer (str)
        
        r_hidden: list (of str, of size l_hidden)
            list with each layer regularization criteria, options are:

                'l1': Lasso regularization |b|
                'l2': Ridge regularization |b|^2
                'elasticnet': C(L1 - L2)
                'dropout': Randomly (uniform) select N neurons in layer and turn its weight to 0
            
        r_cost: str
            regularization criteria applied to cost function, options are: 
                'l1': Lasso regularization |b|
                'l2': Ridge regularization |b|^2
                'elasticnet': C(L1 - L2)

        """
        
        # Number of neurons per hidden layer
        self.hidden_l = hidden_l

        # Activation of hidden layers
        self.hidden_a = hidden_a

        # Number of neurons in output layer
        self.output_n = output_n

        # Activation of output layer (str)
        self.output_a = output_a

        # Cost function definition
        self.cost_f = cost_f

        # Regularization criteria for cost function
        self.cos_rt = cost_r

        # Regularization criteria for hidden layer
        self.hidden_r = hidden_r
    
    # --------------------------------------------------------------------------------- LAYERS FORMATION -- #
    # -------------------------------------------------------------------------------------------------- -- #

    def _formation(self):
        """
        Neural Network Model Topology Formation.        
        """

        # Hidden layers
        self.layers = {'hl_' + str(layer): {'W': {}, 'b':{}, 'a': {}, 'r':{}}
                       for layer in range(0, len(self.hidden_l))}

        # Output layer
        self.layers.update({'ol': {'a': self.output_a, 'W': {}, 'b': {} }})   

        # iterative layer formation loop
        for layer in range(0, len(self.hidden_l)):

            # layer neurons composition
            self.layers['hl_' + str(layer)]['W'] = None

            # layer biases
            self.layers['hl_' + str(layer)]['b'] = None

            # layer activation
            # if only 1 activation function was provided, use it for all hidden layers
            act = self.hidden_a[0] if len(self.hidden_a) == 1 else self.hidden_a[layer]
            self.layers['hl_' + str(layer)]['a'] = act

            # layer regularization
            self.layers['hl_' + str(layer)]['r'] = None

            # layer weights initialization
            self.layers['hl_' + str(layer)]['i'] = ''

    # --------------------------------------------------------------------------- WEIGHTS INITIALIZATION -- #
    # -------------------------------------------------------------------------------------------------- -- #

    def init_weights(self, input_shape, init_layers):
        """
        Weight initialization
        
        Parameters
        ----------

        input_shape: int
            number of features (inputs) in the model
                
        init_layers: list (of str, with size of n_layers)
        
            list with each layer criteria for weights initialization, with options: 

                'common-uniform': Commonly used factor & uniformly distributed random weights [1]
                'xavier_uniform': Xavier factor & uniformly distributed random weights [1]
                'xavier_normal': Xavier factor & standard-normally distributed random weights [1]            
                'he-standard': Factor [2]
        
        References
        ----------
        
        [1] X. Glorot and Y. Bengio.  Understanding the difficulty oftraining deep feedforward neural   
            networks. International Conference on Artificial Intelligence and Statistics, 2010.
        
        [2] He et al. "Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet 
            Classification," 2015 IEEE International Conference on Computer Vision (ICCV), 2015, pp. 1026-1034, doi: 10.1109/ICCV.2015.123.

        """

        # reproducibility
        np.random.seed(2)

        # base topology formation
        self._formation()

        # number of hidden layers
        layers = len(self.hidden_l)

        # hidden layers weights
        for layer in range(0, layers):

            # if only one weight initialization criteria is specified, use it for all layers.
            if len(init_layers) == 1 and len(self.hidden_l):
                init_layers = [init_layers[0]]*len(self.hidden_l)

            # type of initialization for each layer
            type = init_layers[layer]

            # store the type of initialization used for each layer
            self.layers['hl_' + str(layer)]['i'] = type

            # number of Neurons in layer
            nn = self.hidden_l[layer]

            # multiplication factor (depends on the activation function) according to [1]
            mf = 4 if self.layers['hl_' + str(layer)]['a'] == 'tanh' else 1

            # check input dimensions for first layer
            if layer == 0:
                n_prev = input_shape
                n_next = self.hidden_l[layer]
            
            # following layers are the same
            else:
                n_prev = self.hidden_l[layer-1]
                n_next = self.hidden_l[layer]

            # As mentioned in [1]
            if type == 'common-uniform':
                
                # Boundaries according to uniform distribution common heuristic
                r = mf * np.sqrt(1/nn)
                
                # Hidden layer weights and bias
                self.layers['hl_' + str(layer)]['W'] = np.random.uniform(-r, r, size=(n_next, n_prev))
                
                # Output layer
                self.layers['ol']['W'] = np.random.uniform(-r, r, size=(self.output_n, self.hidden_l[-1]))
                
                # Bias weigths in zero
                self.layers['hl_' + str(layer)]['b'] = np.zeros((nn, 1))
                self.layers['ol']['b'] = np.zeros((self.output_n, 1))

            # According to eq:16 in [1]
            elif type == 'xavier-uniform':
                
                # Boundaries according to uniform distribution common heuristic
                r = mf * np.sqrt(6/(n_prev + n_next))
                
                # Hidden layer weights and bias
                self.layers['hl_' + str(layer)]['W'] = np.random.uniform(-r, r, size=(n_next, n_prev))

                # Output layer
                self.layers['ol']['W'] = np.random.uniform(-r, r, size=(self.output_n, self.hidden_l[-1]))
                
                # Bias weigths in zero
                self.layers['hl_' + str(layer)]['b'] = np.zeros((nn, 1))
                self.layers['ol']['b'] = np.zeros((self.output_n, 1))

            # A variation of the previous, according to [1]
            elif type == 'xavier-standard':
                
                # Multiplying factor (paper version)
                # r = mf * np.sqrt(2/(n_prev + n_next))
                # Multiplying factor (coursera Deeplearning version)
                r = 0.01
                
                # Hidden layer weights and biasW
                self.layers['hl_' + str(layer)]['W'] = np.random.randn(n_next, n_prev) * r
                
                # Output layer
                self.layers['ol']['W'] = np.random.randn(self.output_n, self.hidden_l[-1]) * r
                
                # Bias weigths in zero
                self.layers['hl_' + str(layer)]['b'] = np.zeros((nn, 1))
                self.layers['ol']['b'] = np.zeros((self.output_n, 1))

           # According to [2]
            elif type == 'he-standard':
                
                # Multiplying factor
                r = mf * np.sqrt(2/(n_prev + n_next))
                
                # Hidden layer weights and bias
                self.layers['hl_' + str(layer)]['W'] = np.random.randn(n_next, n_prev) * r
                
                # Output layer
                self.layers['ol']['W'] = np.random.randn(self.output_n, self.hidden_l[-1]) * r

                # Bias weigths in zero
                self.layers['hl_' + str(layer)]['b'] = np.zeros((nn, 1))
                self.layers['ol']['b'] = np.zeros((self.output_n, 1))

            else: 
                print('Raise Error')

    # ------------------------------------------------------------------ FIT MODEL PARAMETERS (LEARNING) -- #
    # -------------------------------------------------------------------------------------------------- -- #

    def fit(self, data, epochs, lr):
        """
        """

        from functions import sigma, d_sigma

        X_train = data['x']
        y_train = data['y'].astype(np.int)
       
        # -------------------------------------------------------------------------------------- FORWARD -- #

        def forward(self, A, l):
            layer = list(self.layers.keys())[l]
            W = self.layers[layer]['W']
            b = self.layers[layer]['b']
            return np.dot(W, A) + b

        def forward_activation(self, A_prev, l):
            layer = list(self.layers.keys())[l]

            Z = forward(self, A_prev, l)
            A = sigma(Z, self.layers[layer]['a'])

            return A, Z

        def forward_propagate(self, X): 
            Al = X.T
            
            # memory to store all the values for later use in backward process
            memory = {'A_' + str(i): 0 for i in range(1, len(self.hidden_l) + 3)}
            memory.update({'Z_' + str(i): 0 for i in range(1, len(self.hidden_l) + 2)})
            memory.update({'d_' + str(i): 0 for i in range(2, len(self.hidden_l) + 3)})
            memory.update({'dW_' + str(i): 0 for i in range(1, len(self.hidden_l) + 2)})
            memory.update({'db_' + str(i): 0 for i in range(1, len(self.hidden_l) + 2)})

            memory['A_' + str(1)] = X.T

            for l in range(0, len(self.hidden_l) + 1):
                A_prev = Al
                Al, Zl = forward_activation(self, A_prev, l)
                
                # save A and Z for every layer (for backward process)
                memory['Z_' + str(l + 1)] = Zl
                memory['A_' + str(l + 2)] = Al.T

            return memory

        # ------------------------------------------------------------------------------------- BACKWARD -- #


        def backward_propagate(self, memory, Y):
            
            # get the post-activation values for the last layer
            AL = memory['A_' + str(len(self.hidden_l) + 2)]
            # Y = Y.reshape(AL.shape)
            
            # first delta for the output layer
            dAL = (1/AL.shape[1]) * (AL - Y)
            memory['d_' + str(len(self.hidden_l) + 2)] = dAL

            # just loop hidden layers since the above was for the outputlayer
            for l in range(len(self.hidden_l) - 1 , -1, -1):

                layer = list(self.layers.keys())[l + 0]

                # dW previous layer
                dW = memory['d_' + str(l + 3)] * memory['A_' + str(l + 2)]
                memory['dW_' + str(l + 2)] = dW
                memory['db_' + str(l + 2)] = memory['d_' + str(l + 3)].sum()
                
                d = np.dot((memory['A_' + str(l + 2)] * memory['d_' + str(l + 3)]), self.layers[layer]['W'])
                memory['d_' + str(l + 2)] = d
            
            # last delta for the input layer
            memory['dW_' + str(1)] = np.dot(memory['d_' + str(2)].T, memory['A_' + str(1)].T)
            memory['db_' + str(1)] = memory['d_' + str(2)].sum()

            return memory

        # ----------------------------------------------------------------------------- GRADIENTS UPDATE -- #

        def update_grads(self, memory):

            for l in range(1, len(self.hidden_l) + 2):

                layer  = list(self.layers.keys())[l - 1]               
                dW = memory['dW_' + str(l)]
                db = memory['db_' + str(l)]

                self.layers[layer]['W'] = self.layers[layer]['W'] - lr*dW
                self.layers[layer]['b'] = self.layers[layer]['b'] - lr*db
       
        # ------------------------------------------------------------------------------ TRAINING EPOCHS -- #
        
        J = {}
        for epoch in range(epochs):
            
            memory = forward_propagate(self, X_train)
            Al = memory['A_3']
            cost = fn.cost(Al, data['y'], 'sse')
            print(cost)
            J[epoch] = cost
            bwd = backward_propagate(self, memory, y_train)

            update_grads(self,bwd)

        print('Final cost:', J[epochs-1])
        
        return J

    # ------------------------------------------------------------------------------- PREDICT WITH MODEL -- #
    # -------------------------------------------------------------------------------------------------- -- #

    def predict(self):
        """
        """

        return 1
