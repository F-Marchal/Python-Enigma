This project has for goal to create an enigma in Python. 

If you do not know anything about Enigma, I highly recommend the website of the Crypto Museum:
- https://www.cryptomuseum.com/

You will find in the file “Historical.py” Rotor, Reflectors (UKW) and Machine that have been used in the past. All the information presents inside this file come from : https://www.cryptomuseum.com/crypto/enigma/wiring.htm

# Objects 
- Rotor : Is made to emulate a rotors used by Enigma:
- ETW : A Special kind of Rotor that represent the entry wheels (the element that link the keyboard and the rotor)
- Reflector : A Special kind of rotor that can be used as reflector (UKW). The wiring of this king of rotor has to be "symmetrical".

- EnigmaMachine : The main object of this package. This object require the creation of Rotors object to  work as intended.

# Future goals :
- Improve docString clarity
- Improve machine speed
- Add an “how to use” section.

# About
I have worked on this project during my free time for my own amusement. I can’t guaranty that I will update this project frequently.
