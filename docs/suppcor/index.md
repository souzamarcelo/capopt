---
layout: template
title: Supplementary page [capopt]
---

Supplementary page to the paper:

# Capping Methods for the Automatic Configuration of Optimization Algorithms

[Marcelo de Souza][marcelo]{:target="_blank"}, [Marcus Ritt][marcus]{:target="_blank"} and [Manuel López-Ibáñez][manuel]{:target="_blank"}<br>
Computers & Operations Research, 2020

***

## Abstract

Automatic configuration techniques are widely and successfully used to find good parameter settings for parameterized algorithms. Configuration is costly, because it is necessary to evaluate many configurations on different instances. For decision problems, when the objective is to minimize the running time of the algorithm, many configurators implement capping methods to discard poor configurations early. Such methods are not directly applicable to optimization problems, when the objective is to optimize the cost of the best solution found, given a predefined running time limit. We propose new capping methods for the automatic configuration of optimization algorithms. They use the previous executions to determine a performance envelope, which is used to evaluate new executions and cap those that do not satisfy the envelope conditions. We integrate the capping methods into the irace configurator and evaluate them on different optimization scenarios. Our results show that the proposed methods can save from about 5% to 80% of the configuration effort, while finding configurations of the same quality. Based on the computational analysis, we identify two conservative methods, that save an average of about 20% of the configuration effort and never found significantly worse configurations than those obtained without capping on all tested problems. We also provide evidence that capping can help to better use the available budget in scenarios with a configuration time limit.

**Keywords:** automatic algorithm configuration; capping methods; optimization algorithms; parameter tuning

***

## capopt

All capping methods are implemented in capopt. It provides a Python target runner script that integrates with irace. All details of how to use it is provided in the [project website][capopt]{:target="_blank"}. The source code is available in the [GitHub repository of capopt][capopt-github]{:target="_blank"}. You can download the exact version used in our experiments [here][capopt-download]{:target="_blank"}.

***

## Configuration Scenarios

We tested the capping methods in the following scenarios:

+ ACOTSP: ant colony optimization algorithms for the symmetric traveling salesperson problem [1].
+ HEACOL: hybrid evolutionary algorithm for graph coloring [2].
+ TSBPP: tabu search for the bin packing problem [3, 4].
+ HHBQP: hybrid heuristic for unconstrained binary quadratic programming [5].

Below you find all files to replicate our experiments:

| Scenario | Source code&nbsp;<sup>1,&nbsp;2</sup>      | Parameters                                            | Train instances                                    | Test instances                                   | Best known values                              | Param. target runner&nbsp;<sup>3</sup>                                 | Scenario file&nbsp;<sup>4</sup>                                | Cut-off effort          | Budget (execs) | Budget (time) |
|----------|--------------------------------------------|-------------------------------------------------------|----------------------------------------------------|--------------------------------------------------|------------------------------------------------|------------------------------------------------------------------------|----------------------------------------------------------|-------------------------|----------------|---------------|
| ACOTSP   | [acotsp.zip][src-acotsp]{:target="_blank"} | [parameters-acotsp.txt][par-acotsp]{:target="_blank"} | [train-acotsp.zip][train-acotsp]{:target="_blank"} | [test-acotsp.zip][test-acotsp]{:target="_blank"} | [bkv-acotsp.txt][bkv-acotsp]{:target="_blank"} | [parameters-capopt-acotsp.txt][parc-acotsp]{:target="_blank"} | [scenario-acotsp.txt][scenario-acotsp]{:target="_blank"} | 60 sec.                 | 2000           | 21000 sec.    |
| HEACOL   | [heacol.zip][src-heacol]{:target="_blank"} | [parameters-heacol.txt][par-heacol]{:target="_blank"} | [train-heacol.zip][train-heacol]{:target="_blank"} | [test-heacol.zip][test-heacol]{:target="_blank"} | [bkv-heacol.txt][bkv-heacol]{:target="_blank"} | [parameters-capopt-heacol.txt][parc-heacol]{:target="_blank"} | [scenario-heacol.txt][scenario-heacol]{:target="_blank"} | 10<sup>9</sup> checks   | 2000           | 3200 sec.     |
| TSBPP    | [tsbpp.zip][src-tsbpp]{:target="_blank"}   | [parameters-tsbpp.txt][par-tsbpp]{:target="_blank"}   | [train-tsbpp.zip][train-tsbpp]{:target="_blank"}   | [test-tsbpp.zip][test-tsbpp]{:target="_blank"}   | [bkv-tsbpp.txt][bkv-tsbpp]{:target="_blank"}   | [parameters-capopt-tsbpp.txt][parc-tsbpp]{:target="_blank"}   | [scenario-tsbpp.txt][scenario-tsbpp]{:target="_blank"}   | 5000 iterations         | 500            | 700 sec.      |
| HHBQP    | [hhbqp.zip][src-hhbqp]{:target="_blank"}   | [parameters-hhbqp.txt][par-hhbqp]{:target="_blank"}   | [train-hhbqp.zip][train-hhbqp]{:target="_blank"}   | [test-hhbqp.zip][test-hhbqp]{:target="_blank"}   | [bkv-hhbqp.txt][bkv-hhbqp]{:target="_blank"}   | [parameters-capopt-hhbqp.txt][parc-hhbqp]{:target="_blank"}   | [scenario-hhbqp.txt][scenario-hhbqp]{:target="_blank"}   | 20/30 sec. (train/test) | 2000           | 7000 sec.     |

<sup>1</sup> We modified the source code of all target algorithms to make them printing the solution costs (and the used effort, when applicable) during the execution.<br>
<sup>2</sup> You can acces the original source code of all scenarios: [ACOTSP][acotsp]{:target="_blank"}, [HEACOL][heacol]{:target="_blank"}, [TSBPP][tsbpp]{:target="_blank"}, [HHBQP][hhbqp]{:target="_blank"}.<br>
<sup>3</sup> The *parameters-capopt* file is an example that uses the *AD.2* capping method (area-based adaptive method with a<sub>g</sub>= 0.2).<br>
<sup>4</sup> The *scenario.txt* file is an example that uses a seed equals to 1114706456.

***


## Generated Data

Below you find the raw data of our experiments:
+ Evaluation of all capping methods [[train-data-evaluation.csv][train-data-evaluation]{:target="_blank"} \| [test-data-evaluation.csv][test-data-evaluation]{:target="_blank"}]
+ Analysis of selected methods (9th replication on ACOTSP) [[noncapped-executions.csv][noncapped]{:target="_blank"} \| [capped-executions.csv][capped]{:target="_blank"}]
+ Time as budget experiment [[train-data-timeasbudget.csv][train-data-timeasbudget]{:target="_blank"} \| [test-data-timeasbudget.csv][test-data-timeasbudget]{:target="_blank"}]

***


## References

[1] Dorigo, M., Stützle, T., 2004. Ant Colony Optimization. MIT Press, Cambridge, MA.

[2] Galinier, P., Hao, J.K., 1999. Hybrid evolutionary algorithms for graph coloring. Journal of Combinatorial Optimization 3, 379–397.

[3] Lodi, A., Martello, S., Vigo, D., 1999. Heuristic and metaheuristic approaches for a class of two-dimensional bin packing problems. INFORMS Journal on Computing 11, 345–357.

[4] Lodi, A., Martello, S., Vigo, D., 2004a. TSpack: a unified tabu search code for multi-dimensional bin packing problems. Annals of Operations Research 131, 203–213.

[5] De Souza, M., Ritt, M., 2018. Automatic grammar-based design of heuristic algorithms for unconstrained binary quadratic programming, in: Evolutionary Computation in Combinatorial Optimization, Springer International Publishing. pp. 67–84.


[marcelo]: https://souzamarcelo.github.io
[marcus]: https://www.inf.ufrgs.br/~mrpritt
[manuel]: http://lopez-ibanez.eu
[capopt]: https://capopt.github.io
[capopt-github]: https://github.com/capopt/capopt
[capopt-download]: files/capopt.zip
[acotsp]: http://www.aco-metaheuristic.org/aco-code/public-software.html
[heacol]: http://rhydlewis.eu/resources/gCol.zip
[tsbpp]: http://or.dei.unibo.it/research_pages/ORcodes/TSpack.html
[hhbqp]: https://github.com/souzamarcelo/hhbqp
[src-acotsp]: files/acotsp.zip
[src-heacol]: files/heacol.zip
[src-tsbpp]: files/tsbpp.zip
[src-hhbqp]: files/hhbqp.zip
[par-acotsp]: files/parameters-acotsp.txt
[par-heacol]: files/parameters-heacol.txt
[par-tsbpp]: files/parameters-tsbpp.txt
[par-hhbqp]: files/parameters-hhbqp.txt
[bkv-acotsp]: files/bkv-acotsp.txt
[bkv-heacol]: files/bkv-heacol.txt
[bkv-tsbpp]: files/bkv-tsbpp.txt
[bkv-hhbqp]: files/bkv-hhbqp.txt
[train-acotsp]: files/train-acotsp.zip
[train-heacol]: files/train-heacol.zip
[train-tsbpp]: files/train-tsbpp.zip
[train-hhbqp]: files/train-hhbqp.zip
[test-acotsp]: files/test-acotsp.zip
[test-heacol]: files/test-heacol.zip
[test-tsbpp]: files/test-tsbpp.zip
[test-hhbqp]: files/test-hhbqp.zip
[parc-acotsp]: files/parameters-capopt-acotsp.txt
[parc-heacol]: files/parameters-capopt-heacol.txt
[parc-tsbpp]: files/parameters-capopt-tsbpp.txt
[parc-hhbqp]: files/parameters-capopt-hhbqp.txt
[scenario-acotsp]: files/scenario-acotsp.txt
[scenario-heacol]: files/scenario-heacol.txt
[scenario-tsbpp]: files/scenario-tsbpp.txt
[scenario-hhbqp]: files/scenario-hhbqp.txt
[train-data-evaluation]: files/train-data-evaluation.csv
[test-data-evaluation]: files/test-data-evaluation.csv
[train-data-timeasbudget]: files/train-data-timeasbudget.csv
[test-data-timeasbudget]: files/test-data-timeasbudget.csv
[noncapped]: files/noncapped-executions.csv
[capped]: files/capped-executions.csv
