# Michelson Interferometer

## Goals (few but good):
- build the setup successfully to see the fringes on the screen
- measure the speed of light _c_ in air

## The experiment in a few words
A laser points into a beamsplitter, both split beams are reflected back to the beam splitter and the resulting superposed light beam is projected onto a detector/screen producing an interference pattern due to the slightly different direction of the two beams. By moving the second mirror, the phase of the resulting light wave changes and the pattern moves on the screen consequently.

## Working principle
The mirrors don't reflect the light exactly with a 0 degree angle else the light would already interfere with itself there. This means that when the two beams get back together they have slightly different directions meaning the two wavefronts are not aligned => the resulting wavefront is not flat => we see a pattern.

By changing the distance between the second mirror and the beamsplitter by ${ \Delta l }$, we can increase the optical path of the second beam by a factor of ${ 2 \Delta l }$ creating a phase of ${ 2 k \Delta l }$ in the resulting beam.

A continuous increase of the mirror distance (i.e. the optical path of the second beam) results in a continuous propagation of the projected pattern, where a full cycle in the pattern movement corresponds to half a wavelength shift of the mirror (i.e. one wavelength increase in the optical path of the second beam).

cfr. https://www.youtube.com/watch?v=aRvjULwOhmM

## Setup 
Our setup includes:
- optical table
- laser
- beamsplitter
- two mirrors
- linear stage movable with a screw
- diverging lens
- projecting screen
- light detector
- picoscope 
- multifunction counter

## Additional goals 

### Linear stage
If (when) the first setup works (will have worked) we could (will) build an extention of the moving stage mechanism that allows us to increase the precision and the stability of the movement, to enhance the quality of the measurements.

### Measure sound waves with the setup (proposition by Pepe)
Using a very thin layer we can install the second mirror onto this membrane to then capture the vibrations of it from the output signal (analysing the deflection of the signal from a relative initial position of the pattern).

## Formulas
To find the speed of light _c_, knowing ${ \Delta l }$ and _n_:

${ 2 \pi n = \delta \varphi = 2 k \Delta l }$

${ 2 \pi n = 2 \frac{2 \pi}{\lambda} \Delta l }$

${ 2 \pi n = 2 \frac{2 \pi f}{c} \Delta l }$

${ c = \frac{2 f \Delta l}{n} }$

