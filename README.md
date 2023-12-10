# labscript-qc example

This template allows you to set up your machine for remote control through the qiskit-cold-atoms + qlued + labscript-qc pipeline. If you would just like to get a feeling how it would be to have it registered, feel free to add it into [Alqor](https://qlued.alqor.io). But we strongly would like to encourage others to set up their own instances and give it a try.

## Setup and installation

- Clone the repository into the `.../userlib/labscriptlib/EXPERIMENT-NAME` folder.
- Adapt the `connection_table.py` such that it defines the proper connections between the different devices.
- Adapt the `header.py` such that it defines the proper connections and functions.
- Adapt the `config.py` such that it defines all the relevant gates that you would like to expose to the enduser. This is the first non-standard labscript code that you will have to write. 

## Join us in discussions

We use GitHub Discussions to talk about all sorts of topics related to documentation and this site. For example: if you'd like help troubleshooting a PR, have a great new idea, or want to share something amazing you've learned in our docs, join us in the [discussions](https://github.com/Alqor-UG/labscript-qc/discussions).

## License

Any code within this repo is licenced under the [Apache 2](LICENSE) licence.


The qlued documentation in the docs folders are licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).


## Thanks :purple_heart:

Thanks for all your contributions and efforts towards improving qlued. We thank you for being part of our :sparkles: community :sparkles:!