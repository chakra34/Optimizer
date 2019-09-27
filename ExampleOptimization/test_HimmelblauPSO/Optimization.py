#!/usr/bin/env python3

# defining the class name

import numpy as np
import sys,time
import math
import random
import concurrent.futures

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
               restart = False,
               concise_outputs= True,
               points_rs      = None,
               localbest_rs   = None,
               velocities_rs  = None,
               gbest_rs       = None,
               posPBest_rs    = None,
               posGBest_rs    = None,
               pOrder_rs      = None,
               ):
# =====================================================
    self.concise        = concise_outputs
    self.method         = method if method in self._methods else sys.exit()
    self.dimension      = len(bounds)
    self.bounds         = np.array(bounds)                                                # min,max
    self.tolerance      = tolerance
    self.rigid          = rigid                                                           # to determine whether the bound is fixed or not
    self.restart        = restart
    self.points         = None
    self.points_rs      = points_rs                                                       # nest generation points
    self.fitnesses      = None
    self.generation     = 0
    self.root           = root
    self.locations      = {}
    self.curr_locations = []                                                              # array of points, posPBest, velocieties, localBest, pOrder, and fitness for current generation, N*(self.dimension*3+2) matrix  
    if self.method == self._methods[1]:                                                   # pso
      self.localbest      = None                                                          # array of history best fitnesses in each particle
      self.velocities     = None
      self.gbest          = None                                                          # history global best fitness 
      self.posPBest       = None                                                          # particle history best pos
      self.posGBest       = None                                                          # global history best pos
      self.pOrder         = None
      self.localbest_rs   = localbest_rs                                                  # current generation array of history best fitnesses in each particle
      self.velocities_rs  = velocities_rs                                                 # current generation velocities
      self.gbest_rs       = gbest_rs                                                      # current generation history global best fitness 
      self.posPBest_rs    = posPBest_rs                                                   # current generation particle history best pos
      self.posGBest_rs    = posGBest_rs                                                   # current generation global history best pos
      self.pOrder_rs      = pOrder_rs
      self.packages       = None
      
# =====================================================
  def __repr__(self):
# =====================================================
    b = np.nanargmin(self.fitnesses)
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
    b = np.nanargmin(self.fitnesses)
    return self.map2space(self.points[b]),self.fitnesses[b]

# =======================================================
  def cost(self):
# =======================================================
    return len(self.locations)

# =====================================================
  def makeRigid(self,x):
# =====================================================
    return np.minimum(np.maximum(x,np.zeros(self.dimension)),np.ones(self.dimension))             #clip positions

# =====================================================
  def fallBack(self,x):
# =====================================================
    cog_simplex = np.average(self.points,axis=0)
    print ("===== fall back ====")
    print ("x input",x)
    out =  x + np.random.random() * (cog_simplex - x)                                             # random step towards center of simplex
    print ("out",out)
    return out
 
# =====================================================
  def initPopulation(self,N = None):
# =====================================================
    if   self.method == self._methods[0]: self.initPopulation_NM()                                                  # Nelder--Mead  
    elif self.method == self._methods[1]: self.initPopulation_PSO()
    elif self.method == self._methods[2]: self.initPopulation_GA()
    #----------- bounding box ----------------------#
    with open("{}/output_{}.log".format(self.root,self.method),'a') as file:
      file.write(("\n################################ Initial simplex ###########################################") )
      file.write("\n {}".format(self.points))
      file.write("\n ############################################################################################") 
    
# =====================================================
  def initPopulation_NM(self,N = None):
# =====================================================
    ### generate initial point population in parameter space within bounds  
    N = N if N else self.dimension+1
    self.points = self.points_rs if self.restart else np.random.uniform(size=N*self.dimension).reshape(N,self.dimension)
    current_fitnesses = []
    print (" Initial simplex mapped ")
    print (np.array([self.map2space(i) for i in self.points]))
    for i in range(len(self.points)):
      curr_fitness = self.fitness(self.points[i])
      while np.isnan(curr_fitness):
        self.points[i] = self.fallBack(self.points[i])
        self.points[i] = self.makeRigid(self.points[i]) if self.rigid else self.points[i]
        curr_fitness = self.fitness(self.points[i])
      current_fitnesses.append(curr_fitness)
    self.fitnesses = np.array(current_fitnesses)
    
    if not self.concise:
      with open("{}/{}_points{}.txt".format(self.root,self.method,self.generation+1),'w') as fpoints:
        fpoints.write('2 head \n')
        fpoints.write('Generation 1 \n') 
        for i in range(self.dimension):
          fpoints.write('{}_pos '.format(i+1))
        fpoints.write('\n')  
        np.savetxt(fpoints, self.points, delimiter=' ', newline='\n')
       
    current_locations = np.array([self.map2space(i) for i in self.points])
    print('parameters \n {}'.format(current_locations))
    with open("{}/snapshots_{}.txt".format(self.root,self.method),'w') as snapshot:
      snapshot.write('Generation {}\n'.format(self.generation+1))
      snapshot.write('parameters\n')
      snapshot.write('{}\n'.format(current_locations))
      snapshot.write('points\n')
      snapshot.write('{}\n'.format(self.points))
      snapshot.write('fitnesses\n')
      snapshot.write('{}\n'.format(self.fitnesses))
      snapshot.write('##################################################\n')
      
      
# =====================================================
  def initPopulation_PSO(self,N = None):
# =====================================================      

    N = 20                                                                                   # N should be larger than 1 at all time
    self.points = self.points_rs if self.restart else np.random.uniform(size=N*self.dimension).reshape(N,self.dimension)
    print (" Initial population is ")
    print (np.array([self.map2space(i) for i in self.points]))
    self.curr_locations = []
    self.gbest          = self.gbest_rs if self.restart else np.inf 
    self.posGBest       = self.posGBest_rs if self.restart else np.ones_like(self.points[0])
    self.localbest      = self.localbest_rs if self.restart else np.array(np.inf  * np.ones(N))
    self.posPBest       = self.posPBest_rs if self.restart else np.zeros_like(self.points)
    self.velocities     = self.velocities_rs if self.restart else np.random.uniform(low=-1.0,high=1.0,size=N*self.dimension).reshape(N,self.dimension)
    self.pOrder         = self.pOrder_rs if self.restart else np.array(np.arange(1,N+1))
    self.packages       = np.concatenate((self.points,self.posPBest,self.velocities,self.localbest.reshape(N,1),self.pOrder.reshape(N,1)),axis=1)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=N) as executor:
      future_to_fitnesses = [executor.submit(self.fitness, i) for i in self.packages]
      self.fitnesses      = np.array([x.result() for x in concurrent.futures.as_completed(future_to_fitnesses)])

    self.points       = np.array([item[:self.dimension] for item in self.curr_locations])
    self.posPBest     = np.array([item[self.dimension:self.dimension*2] for item in self.curr_locations])
    self.velocities   = np.array([item[self.dimension*2:self.dimension*3] for item in self.curr_locations])
    self.localbest    = np.array([item[self.dimension*3] for item in self.curr_locations])
    self.pOrder       = np.array([item[self.dimension*3+1] for item in self.curr_locations])
    self.fitnesses    = np.array([item[self.dimension*3+2] for item in self.curr_locations])                          #update fitnesses and points after all parallel execution finished

    for i in range(len(self.points)):
      if self.fitnesses[i] <= self.localbest[i]:
        self.localbest[i] = self.fitnesses[i]
        self.posPBest[i]  = self.points[i]
      if self.fitnesses[i] <= self.gbest :
        self.gbest = self.fitnesses[i]
        self.posGBest = self.points[i] 

    points2print      = np.array(np.concatenate((self.pOrder.reshape(N,1),self.points),axis=1))
    posPBest2print    = np.array(np.concatenate((self.pOrder.reshape(N,1),self.posPBest),axis=1))
    velocities2print  = np.array(np.concatenate((self.pOrder.reshape(N,1),self.velocities),axis=1))
    
    if not self.concise:
      with open("{}/{}_points{}.txt".format(self.root,self.method,self.generation+1,),'w') as fpoints:
        fpoints.write('2 head \n')
        fpoints.write('Generation 1 \n') 
        fpoints.write('index ')
        for i in range(self.dimension):
          fpoints.write('{}_pos '.format(i+1))
        fpoints.write('\n')  
        np.savetxt(fpoints, points2print, delimiter=' ', newline='\n')  

      with open("{}/{}_pBest{}.txt".format(self.root,self.method,self.generation+1),'w') as posb:
        posb.write('2 head \n')
        posb.write('Generation 1 \n') 
        posb.write('index ')
        for i in range(self.dimension):
          posb.write('{}_pos '.format(i+1))
        posb.write('\n')  
        np.savetxt(posb, posPBest2print, delimiter=' ', newline='\n')
    
      with open("{}/{}_velocities{}.txt".format(self.root,self.method,self.generation+1),'w') as velos:
        velos.write('2 head \n')
        velos.write('Generation 1 \n') 
        velos.write('index ')
        for i in range(self.dimension):
          velos.write('{}_v '.format(i+1))
        velos.write('\n')  
        np.savetxt(velos, velocities2print, delimiter=' ', newline='\n')         

      with open("{}/{}_gBest{}.txt".format(self.root,self.method,self.generation+1),'w') as posg:
        posg.write('2 head \n')
        posg.write('Generation 1 \n') 
        for i in range(self.dimension):
          posg.write('{}_pos '.format(i+1))
        posg.write('\n')  
        np.savetxt(posg, self.posGBest.reshape(1,self.dimension), delimiter=' ', newline='\n') 

    current_locations = np.array([self.map2space(i) for i in self.points])
    with open("{}/snapshots_{}.txt".format(self.root,self.method),'w') as snapshot:
      snapshot.write('\n'.join(['Generation {}'.format(self.generation+1),
                                'pid and points (initiation)',
                                '{}'.format(points2print),
                                'parameters',
                                '{}'.format(current_locations),
                                'fitnesses',
                                '{}'.format(self.fitnesses),
                                'velocities',
                                '{}'.format(self.velocities),
                                'local Best',
                                '{}'.format(self.localbest),
                                'posPBest',
                                '{}'.format(self.posPBest),
                                'gBest',
                                '{}'.format(self.gbest),
                                'posGBest',
                                '{} corresponding parameters:{}'.format(self.posGBest, self.map2space(self.posGBest)),
                                '##################################################',
                               ])+'\n')
                                 
 # =====================================================
  def initPopulation_GA(self,N = None):
# =====================================================       
    N = N if N else 12


# =====================================================
  def updatePopulation(self):
# =====================================================
    if self.method == self._methods[0]: self.updatePopulation_NM()
    elif self.method == self._methods[1]: self.updatePopulation_PSO()
    elif self.method == self._methods[2]: self.updatePopulation_GA()

    return np.nanargmin(self.fitnesses)


#------------------------- neldermead ------------------------------------------------------------- #

# =====================================================
  def updatePopulation_NM(self):
# =====================================================  
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
    fit_reflect   = self.fitness(pnt_reflect) 
    while np.isnan(fit_reflect):
      pnt_reflect = self.fallBack(pnt_reflect)
      fit_reflect = self.fitness(pnt_reflect)
    if fit_reflect < fit_best:                                                                    # new best --> expand simplex further
      pnt_expansion = pnt_centroid*(1.-gamma) + pnt_reflect*gamma
      pnt_expansion = self.makeRigid(pnt_expansion) if self.rigid else pnt_expansion
      fit_expansion = self.fitness(pnt_expansion) 
      while np.isnan(fit_expansion):
        pnt_expansion = self.fallBack(pnt_expansion)
        pnt_expansion = self.makeRigid(pnt_expansion) if self.rigid else pnt_expansion
        fit_expansion = self.fitness(pnt_expansion)
      self.points[rank[-1]]    = pnt_expansion if fit_expansion < fit_reflect else pnt_reflect
      self.fitnesses[rank[-1]] = fit_expansion if fit_expansion < fit_reflect else fit_reflect
    elif fit_reflect < fit_2ndworst:                                                              # better than second worst --> keep
      self.points[rank[-1]]    = pnt_reflect
      self.fitnesses[rank[-1]] = fit_reflect

    else:                                                                                         # still worst --> contract or shrink
      pnt_contract = pnt_centroid*(1.-beta) \
                   + (pnt_reflect if fit_reflect < fit_worst else pnt_worst)*beta                 # contraction
      pnt_contract = self.makeRigid(pnt_contract) if self.rigid else pnt_contract
      fit_contract = self.fitness(pnt_contract) 
      while np.isnan(fit_contract):
        pnt_contract = self.fallBack(pnt_contract)
        pnt_contract = self.makeRigid(pnt_contract) if self.rigid else pnt_contract
        fit_contract = self.fitness(pnt_contract)
      if fit_contract < fit_worst:                                                              # keep?
        self.points[rank[-1]]    = pnt_contract
        self.fitnesses[rank[-1]] = fit_contract
      else:                                                                                     # shrink!
        self.points = pnt_best*np.ones_like(self.points)*(1.-delta) + self.points*delta
        for k in range(len(self.points)):
          self.points[k] = self.makeRigid(self.points[k]) if self.rigid else self.points[k]
        new_fitnesses = []
        for j in rank[1:] :
          curr_fitness = self.fitness(self.points[j])
          while np.isnan(curr_fitness):
            self.points[j] = self.fallBack(self.points[j])
            self.points[j] = self.makeRigid(self.points[j]) if self.rigid else self.points[j]
            curr_fitness = self.fitness(self.points[j])
          new_fitnesses.append(curr_fitness)
        self.fitnesses[rank[1:]] = np.array(new_fitnesses)          # check everyone except for best (who stays)

#------------------ writing snapshots after each generation ----------------------------------------- #
    if not self.concise:
      with open("{}/{}_points{}.txt".format(self.root,self.method,self.generation+1),'a') as fpoints:
        fpoints.write('2 head \n')
        fpoints.write('Generation {} \n'.format(self.generation+1)) 
        for i in range(self.dimension):
          fpoints.write('{}_pos '.format(i+1))
        fpoints.write('\n')  
        np.savetxt(fpoints, self.points, delimiter=' ', newline='\n')  
    
    current_locations = np.array([self.map2space(i) for i in self.points])
    print('parameters \n {}'.format(current_locations))
    with open("{}/snapshots_{}.txt".format(self.root,self.method),'a') as snapshot:
      snapshot.write('\n'.join(['Generation {}'.format(self.generation+1),
                                'parameters',
                                '{}'.format(current_locations),
                                'points',
                                '{}'.format(self.points),
                                'fitnesses',
                                '{}'.format(self.fitnesses),
                                '##################################################',
                            ])+'\n')

        
#---------------------------------------- pso ---------------------------------------------------- #


# =====================================================
  def updatePopulation_PSO(self,N=None):
# =====================================================    
  ## PSO parameters
    N = 20                                                                                        # N should be larger than 1 at all time
    c1                 = 1.494                                                                   #suggested by paper Eberhart and Shi (2001)
    v_max      = 1.0     

#=============== Basic PSO ================================ #

    points_new = np.ones_like(self.points)
    velocities_new = np.ones_like(self.velocities)
    for i in range(len(self.points)):
      Rcoeff1 = random.random()                                                                    #random coefficient between 0 and 1
      Rcoeff2 = random.random()
      viscous_factor = 0.5 + 0.5*random.random()                                                   #suggested by paper Eberhart and Shi (2001)
      
      velocities_new[i] = self.velocities[i]*viscous_factor \
                 + c1* Rcoeff1 * ((self.posPBest[i] if self.localbest[i] < np.inf else self.points[i]) - self.points[i]) \
                 + c1* Rcoeff2 * ((self.posGBest if self.gbest < np.inf else self.points[i]) - self.points[i])
        
      for l in range(self.dimension):
        velocities_new[i,l] = np.clip(velocities_new[i,l], -v_max, v_max)                                 #update velocity for each parameter 
        
      points_new[i] = self.points[i] + velocities_new[i]
      points_new[i] = self.makeRigid(points_new[i]) if self.rigid else points_new[i] 
      velocities_new[i]= np.where(np.logical_or(np.isclose(points_new[i],0.0),
                                                np.isclose(points_new[i],1.0)),0.0,velocities_new[i])

    self.points     = np.array(points_new)
    self.posPBest   = np.array(self.posPBest)
    self.velocities = np.array(velocities_new)
    self.localbest  = np.array(self.localbest) 
    self.pOrder     = np.array(self.pOrder)

    print (" ---------------- new points --------------------------------------- # ")
    print (self.points)
    print (" ------------------------------------------------------------------- # ")

    self.curr_locations = []
    self.packages       = np.concatenate((self.points,self.posPBest,self.velocities,self.localbest.reshape(N,1),self.pOrder.reshape(N,1)),axis=1)
    with concurrent.futures.ThreadPoolExecutor(max_workers=N) as executor:
      future_to_fitnesses = [executor.submit(self.fitness, i) for i in self.packages]
      self.fitnesses      = np.array([x.result() for x in concurrent.futures.as_completed(future_to_fitnesses)])

    self.points       = np.array([item[:self.dimension] for item in self.curr_locations])
    self.posPBest     = np.array([item[self.dimension:self.dimension*2] for item in self.curr_locations])
    self.velocities   = np.array([item[self.dimension*2:self.dimension*3] for item in self.curr_locations])
    self.localbest    = np.array([item[self.dimension*3] for item in self.curr_locations])
    self.pOrder       = np.array([item[self.dimension*3+1] for item in self.curr_locations])
    self.fitnesses    = np.array([item[self.dimension*3+2] for item in self.curr_locations])                          #update fitnesses and points after all parallel execution finished

    for i in range(len(self.points)):
      if self.fitnesses[i] <= self.localbest[i]:
        self.localbest[i] = self.fitnesses[i]
        self.posPBest[i]  = self.points[i]
      if self.fitnesses[i] <= self.gbest :
        self.gbest = self.fitnesses[i]
        self.posGBest = self.points[i] 
    
    points2print      = np.array(np.concatenate((self.pOrder.reshape(N,1),self.points),axis=1))
    posPBest2print    = np.array(np.concatenate((self.pOrder.reshape(N,1),self.posPBest),axis=1))
    velocities2print  = np.array(np.concatenate((self.pOrder.reshape(N,1),self.velocities),axis=1))
    
    if not self.concise:
      with open("{}/{}_points{}.txt".format(self.root,self.method,self.generation+1),'a') as fpoints:
        fpoints.write('2 head \n')
        fpoints.write('Generation {} \n'.format(self.generation+1)) 
        fpoints.write('index ')
        for i in range(self.dimension):
          fpoints.write('{}_pos '.format(i+1))
        fpoints.write('\n')  
        np.savetxt(fpoints, points2print, delimiter=' ', newline='\n')  

      with open("{}/{}_pBest{}.txt".format(self.root,self.method,self.generation+1),'a') as posb:
        posb.write('2 head \n')
        posb.write('Generation {} \n'.format(self.generation+1)) 
        posb.write('index ')
        for i in range(self.dimension):
          posb.write('{}_pos '.format(i+1))
        posb.write('\n')  
        np.savetxt(posb, posPBest2print, delimiter=' ', newline='\n')
    
      with open("{}/{}_velocities{}.txt".format(self.root,self.method,self.generation+1),'a') as velos:
        velos.write('2 head \n')
        velos.write('Generation {} \n'.format(self.generation+1)) 
        velos.write('index ')
        for i in range(self.dimension):
          velos.write('{}_v '.format(i+1))
        velos.write('\n')  
        np.savetxt(velos, velocities2print, delimiter=' ', newline='\n')

      with open("{}/{}_gBest{}.txt".format(self.root,self.method,self.generation+1),'a') as posg:
        posg.write('2 head \n')
        posg.write('Generation {} \n'.format(self.generation+1)) 
        for i in range(self.dimension):
          posg.write('{}_pos '.format(i+1))
        posg.write('\n')  
        np.savetxt(posg, self.posGBest.reshape(1,self.dimension), delimiter=' ', newline='\n')

#----------------------- writing snapshots ---------------------------------------#
    current_locations = np.array([self.map2space(i) for i in self.points])
    with open("{}/snapshots_{}.txt".format(self.root,self.method),'a') as snapshot:
      snapshot.write('\n'.join(['Generation {}'.format(self.generation+1),
                                'pid and points',
                                '{}'.format(points2print),
                                'parameters',
                                '{}'.format(current_locations),
                                'fitnesses',
                                '{}'.format(self.fitnesses),
                                'velocities',                                                  # velocity (after added; take me to here)
                                '{}'.format(self.velocities),
                                'local Best',
                                '{}'.format(self.localbest),
                                'posPBest',
                                '{}'.format(self.posPBest),
                                'gBest',
                                '{}'.format(self.gbest),
                                'posGBest',
                                '{} corresponding parameters:{}'.format(self.posGBest, self.map2space(self.posGBest)),
                                '##################################################',
                               ])+'\n')

#---------------------------------------- ga  ---------------------------------------------------- #

# =====================================================
  def updatePopulation_GA(self):
# =====================================================      
    count = 1
    ## Genetic algorithm
    average_fitness      = np.nanmean(self.fitnesses)
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
      print ("%%%%%%%%%%%%%%%%%%%% added diversity %%%%%%%%%%%%%%%%%%%%%%%")
      self.points[len(self.points)-1,:] = sorted_population[random.randint(to_keep+1,len(self.points)),:]      # adding diversity
    else:
      count += 1
    for i in range(len(self.points)):
      self.points[i] = self.makeRigid(self.points[i])
    self.fitnesses = np.array([self.fitness(self.map2space(x)) for x in self.points])

# =====================================================
  def optimize(self,
               verbose = False):
# =====================================================
  
    self.initPopulation()
    if verbose: print (repr(self))
    while np.count_nonzero(np.isnan(list(self.locations.values()))) == len(list(self.locations.values())): # initialization again if all fitness are nan
      self.generation += 1
      self.initPopulation()
    history_best = np.nanargmin(list(self.locations.values()))
    with open("{}/fitness_results_{}.txt".format(self.root,self.method),'w') as fit:
      fit.write('1 head\n')
      fit.write('Cost Fitness\n')
      fit.write('{} {}\n'.format(self.cost(),list(self.locations.values())[history_best]))

    while list(self.locations.values())[history_best] > self.tolerance and self.cost() <= 500 \
          and np.logical_not(np.all(self.points == self.points[0,:])):                                  # break when all points are the same
      self.generation += 1
      with open("{}/fitness_results_{}.txt".format(self.root,self.method),'a') as fit:                                 #writing twice cost for the first round  
        fit.write('{} {}\n'.format(self.cost(),list(self.locations.values())[history_best]))
      best_pos = self.updatePopulation()
      current_locations = np.array([self.map2space(i) for i in self.points])
      history_best = np.nanargmin(list(self.locations.values()))
      print ("=================== current population ======================")
      print (self.points)
      print ("=============================================================")
      print ("****** the current best fitness is ****",self.fitnesses[best_pos])
      with open("{}/output_{}.log".format(self.root,self.method),'a') as file:
        file.write("\n =================== current population ======================")
        file.write("\n Generation {}".format(self.generation+1))
        file.write("\n parameters")
        file.write("\n {}".format(current_locations))
        file.write('\n points')
        file.write("\n {}".format(self.points))
        file.write("\n=============================================================")
        file.write("\n ****** the current best fitness is **** {}".format(self.fitnesses[best_pos]))
        file.write("\n ****** the current best parameter is **** {}, point is **** {}".format(current_locations[best_pos],self.points[best_pos]))
      if verbose: print (repr(self))


