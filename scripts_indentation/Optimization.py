#!/usr/bin/env python

# defining the class name

import numpy as np
import sys,time

class Optimization:
  
  _methods = ['neldermead',
              'pso',
                    ]

# =====================================================
  def __init__(self,
               method = _methods[0],
               bounds = None,
               tolerance = 0.0,
               root     = None,
               rigid = False,
               ):
# =====================================================
    self.method    = method if method in self._methods else sys.exit()
    self.dimension = len(bounds)
    self.bounds    = np.array(bounds)                                                               # min,max
    self.tolerance = tolerance
    self.rigid     = rigid                                                                          # to determine whether the bound is fixed or not
    self.points    = None
    self.fitnesses = None
    self.cost      = 0
    self.generation= 0
    self.root      = root
    if self.method == self._methods[1]:                                                             # pso
      self.localbest  = None                                                                        # array of positions and fitnesses
      self.velocities = None
    
# =====================================================
  def __repr__(self):
# =====================================================
    b = np.argmin(self.fitnesses)
    items = []
    for i,(f,p) in enumerate(zip(self.fitnesses,self.points)):
      items.append("{}: {} @ {} {}".format(i,f,p,'***' if i == b else ''))
    return '\n'.join(items)
    
# =====================================================
  def best(self):
# =====================================================
    b = np.argmin(self.fitnesses)
    return self.points[b],self.fitnesses[b]
    
# =====================================================
  def initPopulation(self,N = None):
# =====================================================
    ### generate initial point population in parameter space within bounds

    if   self.method == self._methods[0]:                                                           # Nelder--Mead
      N = N if N else self.dimension+1
    elif self.method == self._methods[1]:
      N = N if N else 5

    self.points  = np.random.uniform(size = N*self.dimension).reshape(N,self.dimension)
    self.points *= self.bounds[:,1]-self.bounds[:,0]
    self.points += self.bounds[:,0]

    self.fitnesses = np.array([self.fitness(x) for x in self.points])
    self.cost += N

    if self.method == self._methods[1]:                                                           # PSO: store internal state
      self.velocities = 0.01 * self.points
      self.localbest  = np.hstack((self.points,self.fitnesses.reshape(N,1)))
    

# =====================================================
  def makeRigid(self,x):
# =====================================================
    if self.method == self._methods[0]:
      x = np.minimum(np.maximum(x,self.bounds[:,0]),self.bounds[:,1])
#       for i in xrange(len(self.bounds)):
#         x[i] = self.bounds[i,0] if x[i] < self.bounds[i,0] else x[i]
#         x[i] = self.bounds[i,1] if x[i] > self.bounds[i,1] else x[i]
    return x
# =====================================================
  def fallBack(self,ratio):
# =====================================================
    if self.method == self._methods[0]:
      x = ( (self.bounds[0,0] * (1 + ratio)) + np.random.random() )                                # random number to avoid degeneracy in NelderMead
      return x


# =====================================================
  def updatePopulation(self):
# =====================================================

#------------------------- neldermead ------------------------------------------------------------- #

    if self.method == self._methods[0]:
## Parameters for NM simplex algorithm      
      alpha = -1.0                                                                                  # reflection
      beta  = 0.5                                                                                   # contraction
      gamma = 2.0                                                                                   # expansion
      delta = 0.5                                                                                   # shrinkage
      
      rank          = np.argsort(self.fitnesses)
      pnt_best      = self.points[rank[ 0]]
      pnt_2ndworst  = self.points[rank[-2]]
      pnt_worst     = self.points[rank[-1]]
      pnt_centroid  = (np.sum(self.points,axis=0) - pnt_worst)/self.dimension                  # centroid excluding the worst point
      pnt_reflect   = pnt_centroid*(1.-alpha) + pnt_worst*alpha                                # reflection
      pnt_reflect   = self.makeRigid(pnt_reflect) if self.rigid else pnt_reflect
      fit_best      = self.fitnesses[rank[ 0]]
      fit_2ndworst  = self.fitnesses[rank[-2]]
      fit_worst     = self.fitnesses[rank[-1]]
      fit_reflect   = self.fitness(pnt_reflect); self.cost += 1

      if fit_reflect < fit_best:                                                                    # new best --> expand simplex further
        pnt_expansion = pnt_centroid*(1.-gamma) + pnt_reflect*gamma
        pnt_expansion = self.makeRigid(pnt_expansion) if self.rigid else pnt_expansion
        fit_expansion = self.fitness(pnt_expansion); self.cost += 1
        self.points[rank[-1]]    = pnt_expansion if fit_expansion < fit_reflect else pnt_reflect
        self.fitnesses[rank[-1]] = fit_expansion if fit_expansion < fit_reflect else fit_reflect

      elif fit_reflect < fit_2ndworst:                                                              # better than second worst --> keep
        self.points[rank[-1]]    = pnt_reflect
        self.fitnesses[rank[-1]] = fit_reflect

      else:                                                                                         # still worst --> contract or shrink
        pnt_contract = pnt_centroid*(1.-beta) \
                     + (pnt_reflect if fit_reflect < fit_worst else pnt_worst)*beta                 # contraction
        pnt_contract = self.makeRigid(pnt_contract) if self.rigid else pnt_contract
        fit_contract = self.fitness(pnt_contract); self.cost += 1
        if fit_contract < fit_worst:                                                              # keep?
          self.points[rank[-1]]    = pnt_contract
          self.fitnesses[rank[-1]] = fit_contract
        else:                                                                                     # shrink!
          self.points = pnt_best*np.ones_like(self.points)*(1.-delta) + self.points*delta
          self.points = self.makeRigid(x for x in self.points) if self.rigid else self.points
          self.fitnesses[rank[1:]] = np.array([self.fitness(x) \
                                               for x in self.points[rank[1:]]])          # check everyone except for best (who stays)
          self.cost += len(self.fitnesses)-1
        
#---------------------------------------- pso ---------------------------------------------------- #

    elif self.method == self._methods[1]:
      ## PSO parameters
      inertia_factor     = 0.9
      c1                 = 2.0
      c2                 = 2.0

      self.velocities = self.velocities*inertia_factor \
               + c1*np.random.random() * (self.localbest[:,:-1] - self.points) \
               + c2*np.random.random() * (np.ones_like(self.points) * \
                                          self.localbest[np.argmin(self.localbest[:,-1]),:-1] - self.points)
      # velocity = v_max if velocity > v_max 
      # velocity = v_min if velocity < v_min v_min ?= -v_max 
      self.points += self.velocities
      # self.points[i] = bounds[i,1] for i in np.where( self.points[i] > bounds[i,1] )
      # self.points[i] = bounds[i,0] for i in np.where( self.points[i] < bounds[i,0] )

      self.fitnesses = np.array([self.fitness(x) for x in self.points])
      self.cost += len(self.points)
      
    return np.argmin(self.fitnesses)

# =====================================================
  def optimize(self,
               verbose = False):
# =====================================================
  
    self.initPopulation()
    if verbose: print repr(self)
    best_pos = np.argmin(self.fitnesses)
    
    while self.fitnesses[best_pos] > self.tolerance:
      best_pos = self.updatePopulation()
      print "****** the current best fitness is ****",self.fitnesses[best_pos]
      self.generation += 1
      if verbose: print repr(self)


