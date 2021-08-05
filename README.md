# Pandemic Simulator

A simple model of a virus spreading over a population.
Similar to the visuals presented here: https://www.washingtonpost.com/graphics/2020/health/coronavirus-how-epidemics-spread-and-end/

![Pandemic Simulator Demo](demo/demo.gif)

**Used technologies:** *Python, Matplotlib, NumPy*

## How to Use

Run main.py. When prompted, either use the default COVID-19 paramters or enter custom parameters that describe the virus's spread. The simulation will begin when the parameters are set.

### Requirements

* Node
* MongoDB (MongoDB Atlas or a local server)
* Alpha Vantage API key 
* Twitter API key

### Installation
In both the client and server folders, run:
```
npm install
```

### Executing program
Set the .env files (refer to .env.example files). Ensure a local MongoDB server is running. The default port is `localhost:27017`. In both the server and client folders, run: 
```
npm start
```

## License

This project is licensed under the MIT License - see the LICENSE.md file for details