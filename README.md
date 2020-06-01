# capopt: Capping Methods for the Automatic Configuration of Optimization Algorithms

Welcome to the *capopt* repository! Please visit the [project website](https://capopt.github.io).<br>
[people](#people) |
[download](#download) |
[getting started](#getting-started) |
[example](#example) |
[license](#license) |
[support](#support) |
[documentation](https://capopt.github.io/docs)

***

The main objective of *capopt* is to speed up the automatic configuration of optimization algorithms. It implements several capping methods for optimization scenarios. These methods use the performance of previously seen executions to determine a performance envelope, which is used to evaluate how good a new configuration is during its execution. If a poorly performing configuration is identified, *capopt* stops the execution and returns a penalized result value.

The following article describes *capopt* in detail and present an extensive experimental evaluation. You can also check its [supplementary page](https://capopt.github.io/suppcor) for further experimental details.

> **Capping Strategies for the Automatic Configuration of Optimization Algorithms**<br>
> Marcelo de Souza, Marcus Ritt, and Manuel López-Ibáñez<br>
> Submitted to Computers & Operations Research, 2020.<br>
> [preprint will be available soon | [supplementary page](https://capopt.github.io/suppcor)]

#### Bibtex
```
@article{DeSouzaEtAl2020,
   title   = {Capping Strategies for the Automatic Configuration of Optimization Algorithms},
   author  = {de Souza, Marcelo and Ritt, Marcus and L{\'o}pez-Ib{\'a}{\~n}ez, Manuel},
   journal = {Submitted to Computers \& Operations Research},
   year    = {2020}
}
```

Please, make sure to reference us if you use *capopt* in your research.

***

## People

**Maintainer:** [Marcelo de Souza][marcelo]

**Collaborators:** [Marcus Ritt][marcus] and [Manuel López-Ibáñez][manuel]

**Contact:** marcelo.desouza [at] udesc.br

***

## Download

You can download *capopt* from our [GitHub repository][capopt]. 

### Dependencies

*capopt* is written in [Python 3][python], and uses the following non-standard libraries:

+ [psutil][psutil]
+ [rpy2][rpy2]

If you are using *capopt* with irace, you will need to install the [R software environment][r] and the [irace package][irace].


***

## Getting Started

To use *capopt* with the irace configurator, set the project directory according to the [irace user guide][iracedoc], then follow the steps below:

1. Download *capopt*.

2. Copy the source code (`capopt` folder) to the project directory.
   + *capopt* will replace the `target-runner` script that is used to communicate irace with the target algorithm.

3. Configure the parameter settings of *capopt*.
   + Create a file named `parameters-capopt.txt` in the project directory.
   + Copy the content of [this file](https://capopt.github.io/assets/files/parameters-capopt.txt) and set the corresponding information (make sure to uncomment the properties you set).

4. Configure irace to call capopt as target runner.
   + Include `targetRunner = "./capopt/capopt.py"` in the `scenario.txt` file.

5. If you need, make some adjustements on `capopt.py`. 
   + You can change the `parseOutput` function to handle the target algorithm's output properly.
   + The provided `parseOutput` behaves as follows:
     + In case of using time as effort measure, *capopt* manages the execution time externaly and expects to read only the solution cost (e.g. "1673.44").
     + In case of using another effort measure, *capopt* expects to read the effort and the solution cost separated by a whitespace (e.g. "493 1673.44").

6. **Done!** You can now run irace with *capopt*. You should have a project directory with (at least) the following content:
   + `capopt`: folder containing *capopt*.
   + `instances`: folder containing the training instances.
   + `algorithm`: the target algorithm executable.
   + `parameters.txt`: file defining the parameters to be configured.
   + `scenario.txt`: file defining the input parameters of irace.
   + `parameters-capopt.txt`: file defining the input parameters of *capopt*.

**Important:**
   + The target algorithm must periodically output the cost of the best found solution. This is the only requirement to use *capopt*.
   + In case of difficulties, check the example below, the complete [documentation](https://capopt.github.io/docs), or [contact us](#support).

***

## Example

### Automatic configuration of ACOTSP

The project directory downloaded [here][example-acotsp], containing the following content:
+ `capopt` folder;
+ `instances` folder;
+ `src-acotsp` folder with the source code of ACOTSP;
  + make sure to compile the source code and copy the executable (`acotsp`) to the project directory.
+ `parameters-acotsp.txt` file with the parameter space definition;
+ `parameters-capopt.txt` file;
+ `scenario.txt` file.

The content of `parameters-capopt.txt` is given below. Note that the target algorithm is called using `./acotsp`, and always giving the fixed fixed parameters `-r 1 --quiet`. The instance, seed and effort limit are identified by the commands `-i`, `--seed`,  `-t`, respectively. We are using the running time as effort measure and 20 sec. as effort limit. We are also using the area-based adaptive capping method, with best-so-far penalty strategy and parameters a<sub>g</sub>= 0.4 and &epsilon; = 0.05.

#### parameters-capopt.txt
```
executable: ./acotsp
fixed-params: -r 1 --quiet
instance-command: -i
seed-command: --seed
effort-limit-command: -t
effort-limit: 20
effort-type: time
capping: True
penalty: best-so-far
envelope: area
strategy: adaptive
ag: 0.4
epsilon: 0.05
```

The content of `scenario.txt` is given below. The file indicates the parameters definition, execution directory, training instances directory, configuration budget, and the number of digits for real parameters. The last lilne defined the target runner, which is the *capopt* script.

#### scenario.txt
```
parameterFile = "./parameters-acotsp.txt"
execDir = "."
trainInstancesDir = "./instances"
maxExperiments = 2000
digits = 2
targetRunner = "./capopt/capopt.py"
```

***

## License

This software is Copyright (C) 2020 Marcelo de Souza.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program (see https://github.com/capopt/capopt). If not, see https://www.gnu.org/licenses.

IMPORTANT NOTE: Please be aware that the fact that this program is released as Free Software does not excuse you from scientific propriety, which obligates you to give appropriate credit! If you write a scientific paper describing research that made substantive use of this program, it is your obligation as a scientist to (a) mention the fashion in which this software was used in the Methods section; (b) mention the algorithm in the References section. The appropriate citation is:

+ Marcelo de Souza, Marcus Ritt, and Manuel López-Ibáñez. Capping Strategies for the Automatic Configuration of Optimization Algorithms. Submitted to Computers & Operations Research, 2020.

***

## Support

For any question or suggestion please contact [Marcelo de Souza][marcelo] (marcelo.desouza [at] udesc.br).

[marcelo]: https://souzamarcelo.github.io
[marcus]: https://www.inf.ufrgs.br/~mrpritt
[manuel]: http://lopez-ibanez.eu
[capopt]: https://github.com/capopt/capopt
[python]: https://www.python.org
[r]: https://www.r-project.org
[irace]: http://iridia.ulb.ac.be/irace
[rpy2]: https://rpy2.github.io
[psutil]: https://psutil.readthedocs.io/en/latest
[example-acotsp]: https://github.com/capopt/capopt/tree/master/examples/acotsp
[iracedoc]: https://cran.r-project.org/web/packages/irace/vignettes/irace-package.pdf
