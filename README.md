# 3D Watermarking based on Spectral Decomposition

This repository contains an implementation of the 3D watermarking algorithm proposed by [*Cayre et al*](https://www.sciencedirect.com/science/article/pii/S0923596502001479) based on Spectral Decomposition.

## Getting Started

### Dependencies

This project uses the following packages :

* [*NumPy*](http://www.numpy.org/)
* [*PyMesh*](http://pymesh.readthedocs.io/en/latest/#)

### Installation

All the dependencies needed can be installed with the following command:

```
make init
```

### Usage

The main functions are located inside `sample/spectral_decomposition.py` :

* `insert`
* `extract`

## Running the tests

There is no unit testing implemented at this time. To perform tests, simply run `make tests`. This command will first insert a watermark then read it back and print the number of errors found. The visual deformations introduced by the watermark can be observed by opening the `tests/watermarked_models/out.obj` file.

## Author

* **Antoine Prieëls** - [aprieels](https://github.com/aprieels)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Benoît Macq and Patrice Rondao-Alface for their help during the development