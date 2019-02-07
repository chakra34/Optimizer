#!/usr/bin/env python

# defining the class name

import numpy as np
import sys,time
import math
import random

class Optimization:
  
  _methods = ['neldermead',
              'pso',
              'ga',
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
      self.gbest      = None
      self.posPBest   = None
      self.posGBest   = None
      self.energy     = []
# =====================================================
  def __repr__(self):
# =====================================================
    b = np.argmin(self.fitnesses)
    items = []
    for i,(f,p) in enumerate(zip(self.fitnesses,self.points)):
      items.append("{}: {} @ {} {}".format(i,f,p,'***' if i == b else ''))
    return '\n'.join(items)
    
# =====================================================
  def map2space(self,point):
# =====================================================
    return self.bounds[:,0] + (self.bounds[:,1]-self.bounds[:,0])*point

# =====================================================
  def space2map(self,point):
# =====================================================
    return (point - self.bounds[:,0])/(self.bounds[:,1] - self.bounds[:,0])

# =====================================================
  def best(self):
# =====================================================
    b = np.argmin(self.fitnesses)
    return self.map2space(self.points[b]),self.fitnesses[b]
    
# =====================================================
  def initPopulation(self,N = None):
# =====================================================
    ### generate initial point population in parameter space within bounds

    if   self.method == self._methods[0]:                                                           # Nelder--Mead
      N = N if N else self.dimension+1
      self.points  = np.random.uniform(size = N*self.dimension).reshape(N,self.dimension)
      current_fitnesses = []
      print " Initial simplex mapped "
      print np.array([self.map2space(i) for i in self.points])
      for i in xrange(len(self.points)):
        curr_fitness = self.fitness(self.map2space(self.points[i]))
        while curr_fitness == "none":
          self.points[i] = self.fallBack(self.points[i])
          self.points[i] = self.makeRigid(self.points[i]) if self.rigid else self.points[i]
          curr_fitness = self.fitness(self.map2space(self.points[i]))
        current_fitnesses.append(curr_fitness)
      self.fitnesses = np.array(current_fitnesses)
      with open("{}/snapshots_{}.txt".format(self.root,self.method),'w') as snapshot:
        snapshot.write('Generation {}\n'.format(self.generation))
        snapshot.write('points\n')
        snapshot.write('{}\n'.format(self.points))
        snapshot.write('fitnesses\n')
        snapshot.write('{}\n'.format(self.fitnesses))
        snapshot.write('##################################################\n')
      
      
      
    elif self.method == self._methods[1]:
      N = 20
      self.points = np.random.uniform(size=N*self.dimension).reshape(N,self.dimension)
      print " Initial populaion is "
      print np.array([self.map2space(i) for i in self.points])
      self.fitnesses = np.array([self.fitness(self.map2space(i)) for i in self.points])
      self.velocities = np.random.uniform(size=N*self.dimension).reshape(N,self.dimension)
      self.localbest  = 1e60  * np.ones(N)
      self.posPBest   = np.zeros_like(self.points)
      self.gbest      = 1e60 
      self.posGBest   = np.ones_like(self.points[0])
      with open("{}/snapshots_{}.txt".format(self.root,self.method),'w') as snapshot:
        snapshot.write('Generation {}\n'.format(self.generation))
        snapshot.write('points\n')
        snapshot.write('{}\n'.format(self.points))
        snapshot.write('fitnesses\n')
        snapshot.write('{}\n'.format(self.fitnesses))
        snapshot.write('velocities\n')
        snapshot.write('{}\n'.format(self.velocities))
        snapshot.write('local Best\n')
        snapshot.write('{}\n'.format(self.localbest))
        snapshot.write('posPBest\n')
        snapshot.write('{}\n'.format(self.posPBest))
        snapshot.write('gBest\n')
        snapshot.write('{}\n'.format(self.gbest))
        snapshot.write('posGBest\n')
        snapshot.write('{}\n'.format(self.posGBest))
        snapshot.write('##################################################\n')

    elif self.method == self._methods[2]:
      N = N if N else 12

#----------- bounding box ----------------------#
    with open("{}/output.log".format(self.root),'a') as file:
      file.write(("\n################################ Initial simplex ###########################################") )
      file.write("\n {}".format(self.points))
      file.write("\n ############################################################################################") 
    
# =====================================================
  def makeRigid(self,x):
# =====================================================
    return np.minimum(np.maximum(x,np.zeros(self.dimension)),np.ones(self.dimension))

# =====================================================
  def fallBack(self,x):
# =====================================================
      cog_simplex = np.average(self.points,axis=0)
      print "===== fall back ===="
      print "x input",x
      out =  x + np.random.random() * (cog_simplex - x)                                             # random step towards center of simplex
      print "out",out
      return out



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
      fit_reflect   = self.fitness(self.map2space(pnt_reflect)) #; self.cost += 1
      while fit_reflect == "none":
        pnt_reflect = self.fallBack(pnt_reflect)
        fit_reflect = self.fitness(self.map2space(pnt_reflect))
      if fit_reflect < fit_best:                                                                    # new best --> expand simplex further
        pnt_expansion = pnt_centroid*(1.-gamma) + pnt_reflect*gamma
        pnt_expansion = self.makeRigid(pnt_expansion) if self.rigid else pnt_expansion
        fit_expansion = self.fitness(self.map2space(pnt_expansion)) #; self.cost += 1
        while fit_expansion == "none":
          pnt_expansion = self.fallBack(pnt_expansion)
          pnt_expansion = self.makeRigid(pnt_expansion) if self.rigid else pnt_expansion
          fit_expansion = self.fitness(self.map2space(pnt_expansion))
        self.points[rank[-1]]    = pnt_expansion if fit_expansion < fit_reflect else pnt_reflect
        self.fitnesses[rank[-1]] = fit_expansion if fit_expansion < fit_reflect else fit_reflect
      elif fit_reflect < fit_2ndworst:                                                              # better than second worst --> keep
        self.points[rank[-1]]    = pnt_reflect
        self.fitnesses[rank[-1]] = fit_reflect

      else:                                                                                         # still worst --> contract or shrink
        pnt_contract = pnt_centroid*(1.-beta) \
                     + (pnt_reflect if fit_reflect < fit_worst else pnt_worst)*beta                 # contraction
        pnt_contract = self.makeRigid(pnt_contract) if self.rigid else pnt_contract
        fit_contract = self.fitness(self.map2space(pnt_contract)) #; self.cost += 1
        while fit_contract == "none":
          pnt_contract = self.fallBack(pnt_contract)
          pnt_contract = self.makeRigid(pnt_contract) if self.rigid else pnt_contract
          fit_contract = self.fitness(self.map2space(pnt_contract))
        if fit_contract < fit_worst:                                                              # keep?
          self.points[rank[-1]]    = pnt_contract
          self.fitnesses[rank[-1]] = fit_contract
        else:                                                                                     # shrink!
          self.points = pnt_best*np.ones_like(self.points)*(1.-delta) + self.points*delta
          for k in xrange(len(self.points)):
            self.points[k] = self.makeRigid(self.points[k]) if self.rigid else self.points[k]
          new_fitnesses = []
          for j in rank[1:] :
            curr_fitness = self.fitness(self.map2space(self.points[j]))
            while curr_fitness == "none":
              self.points[j] = self.fallBack(self.points[j])
              self.points[j] = self.makeRigid(self.points[j]) if self.rigid else self.points[j]
              curr_fitness = self.fitness(self.map2space(self.points[j]))
            new_fitnesses.append(curr_fitness)
          self.fitnesses[rank[1:]] = np.array(new_fitnesses)          # check everyone except for best (who stays)

#------------------ writing snapshots after each generation ----------------------------------------- #

      with open("{}/snapshots_{}.txt".format(self.root,self.method),'a') as snapshot:
        snapshot.write('Generation {}\n'.format(self.generation))
        snapshot.write('points\n')
        snapshot.write('{}\n'.format(self.points))
        snapshot.write('fitnesses\n')
        snapshot.write('{}\n'.format(self.fitnesses))
        snapshot.write('##################################################\n')

        
#---------------------------------------- pso ---------------------------------------------------- #

    elif self.method == self._methods[1]:
    ## PSO parameters
      c1                 = 1.2
      viscous_factor     = 0.3

      v_max      = 0.75

      for i in xrange(len(self.points)):
        if self.fitnesses[i] <= self.localbest[i]:
          self.localbest[i] = self.fitnesses[i]
          self.posPBest[i]  = self.points[i]
        if self.fitnesses[i] <= self.gbest :
          self.gbest = self.fitnesses[i]
          self.posGBest = self.points[i]      

      acceleration = np.zeros_like(self.velocities)
      AM_distance = np.ones(self.points.shape[0])
      vel_mag = np.ones_like(self.velocities[:,0])
      current_KE = 0.0
      current_PE = 0.0

#=============== Basic PSO ================================ #

      points_new = np.ones_like(self.points)
      velocities_new = np.ones_like(self.velocities)
      for i in xrange(len(self.points)):
        phi1 = random.random()
        phi2 = random.random()
        vel_mag[i] = math.sqrt(np.dot(self.velocities[i,:],self.velocities[i,:]))

        current_KE += 0.5*vel_mag[i]**2.

        d1 = math.sqrt(np.dot(self.posPBest[i] - self.points[i], 
                                             self.posPBest[i] - self.points[i]))
        d2 = math.sqrt(np.dot(self.posGBest - self.points[i],
                                             self.posGBest - self.points[i]))
        AM_distance[i] = (d1+d2)/2.0
        current_PE += 0.5*c1*AM_distance[i]**2.

        acceleration[i] = c1*( phi1*(self.posPBest[i] - self.points[i]) + phi2*(self.posGBest - self.points[i]) )

        velocities_new[i] = self.velocities[i]*viscous_factor \
                 + c1* phi1 * (self.posPBest[i] - self.points[i]) \
                 + c1* phi2 * (self.posGBest - self.points[i])

        for l in xrange(self.dimension):
          velocities_new[i,l] = min(v_max,velocities_new[i,l])
          
        points_new[i] = self.points[i] + velocities_new[i]

        points_new[i] = self.makeRigid(points_new[i]) if self.rigid else points_new[i]

      self.points = points_new
      self.velocities = velocities_new

      current_KE = current_KE/len(self.velocities)
      self.energy.append(current_KE)
      current_PE = current_PE/len(self.points)
      self.energy.append(current_PE)
      self.energy.append(self.generation)

      print points_new
      print " ---------------- new points --------------------------------------- # "
      print self.points
      print " ------------------------------------------------------------------- # "

      self.fitnesses = np.array([self.fitness(self.map2space(i)) for i in self.points])

#----------------------- writing snapshots ---------------------------------------#

      with open("{}/snapshots_{}.txt".format(self.root,self.method),'a') as snapshot:
        snapshot.write('Generation {}\n'.format(self.generation))
        snapshot.write('points\n')
        snapshot.write('{}\n'.format(self.points))
        snapshot.write('fitnesses\n')
        snapshot.write('{}\n'.format(self.fitnesses))
        snapshot.write('velocities\n')
        snapshot.write('{}\n'.format(self.velocities))
        snapshot.write('local Best\n')
        snapshot.write('{}\n'.format(self.localbest))
        snapshot.write('posPBest\n')
        snapshot.write('{}\n'.format(self.posPBest))
        snapshot.write('gBest\n')
        snapshot.write('{}\n'.format(self.gbest))
        snapshot.write('posGBest\n')
        snapshot.write('{}\n'.format(self.posGBest))
        snapshot.write('##################################################\n')

#---------------------------------------- ga  ---------------------------------------------------- #

    elif self.method == self._methods[2]:
      count = 1
      ## Genetic algorithm
      average_fitness      = np.average(self.fitnesses)
      current_population   = np.hstack((self.points,self.fitnesses.reshape(len(self.points),1) ))
      sorted_population    = current_population[current_population[:,-1].argsort()]
      to_keep              = len(self.points)/2
      parents              = sorted_population[:to_keep,:-1]                                                   # selecting the best points for parents
      desired_children     = len(self.points) - len(parents)
      children             = []
      while len(children) < desired_children:
        crossover_point = 2
        father = parents[random.randint(0,len(parents)-1),:]
        mother = parents[random.randint(0,len(parents)-1),:]
        if np.array_equal(father,mother) == False :
          children.append(np.concatenate((father[:crossover_point],mother[crossover_point:])))
          children.append(np.concatenate((father[crossover_point:],mother[:crossover_point])))
      children = np.array(children).reshape(len(children),self.dimension)
      self.points = np.vstack((parents,children))
      if count%8 == 0:
        print "%%%%%%%%%%%%%%%%%%%% added diversity %%%%%%%%%%%%%%%%%%%%%%%"
        self.points[len(self.points)-1,:] = sorted_population[random.randint(to_keep+1,len(self.points)),:]      # adding diversity
      else:
        count += 1
      for i in xrange(len(self.points)):
        self.points[i] = self.makeRigid(self.points[i])
      self.fitnesses = np.array([self.fitness(self.map2space(x)) for x in self.points])

    return np.argmin(self.fitnesses)

# =====================================================
  def optimize(self,
               verbose = False):
# =====================================================
  
    self.initPopulation()
    if verbose: print repr(self)
    best_pos = np.argmin(self.fitnesses)
    with open("{}/fitness_results.txt".format(self.root),'w') as fit:
      fit.write('1 head\n')
      fit.write('Cost Fitness\n')
      fit.write('{} {}\n'.format(self.cost,self.fitnesses[best_pos]))

    while self.fitnesses[best_pos] > self.tolerance and self.cost <= 200 :
      self.generation += 1
      with open("{}/fitness_results.txt".format(self.root),'a') as fit:
        fit.write('{} {}\n'.format(self.cost,self.fitnesses[best_pos]))
      best_pos = self.updatePopulation()
      print "=================== current population ======================"
      print self.points
      print "============================================================="
      print "****** the current best fitness is ****",self.fitnesses[best_pos]
      with open("{}/output.log".format(self.root),'a') as file:
        file.write("\n =================== current population ======================")
        file.write("\n {}".format(self.points))
        file.write("\n=============================================================")
        file.write("\n ****** the current best fitness is **** {}".format(self.fitnesses[best_pos]))
      if verbose: print repr(self)


