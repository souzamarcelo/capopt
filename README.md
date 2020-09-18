# capopt
**Capping Methods for the Automatic Configuration of Optimization Algorithms**

The *capopt* program implements several capping methods to speed up the automatic configuration of optimization algorithms. These methods use the performance of previously seen executions to determine a performance envelope, which is used to evaluate how good a new configuration is during its execution. If a poorly performing configuration is identified, *capopt* stops the execution and returns a penalized result value.

The following article describes *capopt* in detail and presents an extensive experimental evaluation. You can also check its [supplementary page](https://capopt.github.io/suppcor) for further experimental details.

+ Marcelo de Souza , Marcus Ritt, and Manuel López-Ibáñez. **Capping Strategies for the Automatic Configuration of Optimization Algorithms**. Submitted to Computers & Operations Research, 2020<br>
[preprint will be available soon | [supplementary page](https://capopt.github.io/suppcor)]

#### Bibtex
```bibtex
@article{DeSouzaEtAl2020,
   title   = {Capping Strategies for the Automatic Configuration of Optimization Algorithms},
   author  = {Souza, Marcelo and Ritt, Marcus and L{\'o}pez-Ib{\'a}{\~n}ez, Manuel},
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

## Dependencies

The *capopt* program is written in [Python 3][python], and uses the following non-standard libraries:

+ [psutil][psutil]
+ [rpy2][rpy2]

If you are using *capopt* with irace, you need to install:

+ [R software environment][r]
+ [irace package][irace].

***

## Getting Started

To use *capopt* with the irace configurator, set the project directory according to the [irace user guide][iracedoc], then follow the steps below:

1. Download *capopt*.

2. Copy the source code (`capopt` folder) to the project directory.
   + *capopt* will replace the `target-runner` script that is used to communicate irace with the target algorithm.

3. Configure the parameter settings of *capopt*.
   + Create a file named `parameters-capopt.txt` in the project directory.
   + Copy the content of [this file](examples/parameters-capopt.txt) and set the corresponding information (make sure to uncomment the properties you set).

4. Configure irace to call capopt as target runner.
   + Include `targetRunner = "./capopt/capopt.py"` in the `scenario.txt` file.

5. If you need, make some adjustements on `capopt.py`. 
   + You can change the `parseOutput` function to handle the target algorithm's output properly.
   + The provided `parseOutput` behaves as follows:
     + In case of using time as effort measure, *capopt* manages the execution time externaly and expects to read only the solution cost (e.g. "1673.44").
     + In case of using another effort measure, *capopt* expects to read the effort and the solution cost separated by a whitespace (e.g. "493 1673.44").

6. **Done!** You can now run irace with *capopt*. In summary, you should have a project directory with (at least) the following content:
   + `capopt`: folder containing *capopt*.
   + `instances`: folder containing the training instances.
   + `algorithm`: the target algorithm executable.
   + `parameters.txt`: file defining the parameters to be configured.
   + `scenario.txt`: file defining the input parameters of irace.
   + `parameters-capopt.txt`: file defining the input parameters of *capopt*.

**Important:**
   + The target algorithm must periodically output the cost of the best found solution. This is the only requirement to use *capopt*.
   + In case of difficulties, check the example below or contact us (marcelo.desouza@udesc.br).

***

## Example (ACOTSP)

[This directory][example-acotsp] contains the files for using capping to configure ACOTSP:
+ `capopt` folder;
+ `instances` folder;
+ `src-acotsp` folder with the source code of ACOTSP;
  + make sure to compile the source code and copy the executable (`acotsp`) to the project directory.
+ `parameters-acotsp.txt` file with the parameter space definition;
+ `parameters-capopt.txt` file;
+ `scenario.txt` file.

The content of `parameters-capopt.txt` is given below. Note that the target algorithm is called using `./acotsp`, and always giving the fixed fixed parameters `-r 1 --quiet`. The instance, seed and effort limit are identified by the commands `-i`, `--seed`,  `-t`, respectively. We are using the running time as effort measure and 20 seconds as effort limit. We are also using the area-based adaptive capping method, with best-so-far penalty strategy and parameters a<sub>g</sub>= 0.4 and &epsilon; = 0.05.

**parameters-capopt.txt**
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

The content of `scenario.txt` is given below. The file indicates the parameters definition, execution directory, training instances directory, configuration budget, and the number of digits for real parameters. The last line defined the target runner, which is the *capopt* script.

**scenario.txt**
```
parameterFile = "./parameters-acotsp.txt"
execDir = "."
trainInstancesDir = "./instances"
maxExperiments = 2000
digits = 2
targetRunner = "./capopt/capopt.py"
```

[marcelo]: https://souzamarcelo.github.io
[marcus]: https://www.inf.ufrgs.br/~mrpritt
[manuel]: http://lopez-ibanez.eu
[capopt]: https://github.com/souzamarcelo/capopt
[python]: https://www.python.org
[r]: https://www.r-project.org
[irace]: http://iridia.ulb.ac.be/irace
[rpy2]: https://rpy2.github.io
[psutil]: https://psutil.readthedocs.io/en/latest
[example-acotsp]: https://github.com/capopt/capopt/tree/master/examples/acotsp
[iracedoc]: https://cran.r-project.org/web/packages/irace/vignettes/irace-package.pdf
