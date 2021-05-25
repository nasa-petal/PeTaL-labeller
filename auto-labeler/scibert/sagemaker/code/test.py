from generate import model_fn, input_fn, predict_fn,output_fn
import json

abstract = 'In the marine environment, both external fertilization and settlement are critical processes linking adult and early juvenile life-history phases. The success of both processes can be tightly linked in organisms lacking a larval dispersive phase. This review focuses on synchronous gamete release (= spawning) in fucoid algae. These brown macroalgae are important components of temperate intertidal ecosystems in many parts of the world, and achieve synchronous gamete release by integrating various environmental signals. Photosynthesis-dependent sensing of boundary-layer inorganic carbon fluxes, as well as blue light and green light signals, possibly perceived via a chloroplast-located photoreceptor(s), are integrated into pathways that restrict gamete release to periods of low water motion. Avoidance of turbulent and/or high flow conditions in the intertidal zone allows high levels of fertilization success in this group. Temporal patterns and synchrony of spawning in natural populations are reviewed. Most species/populations have a more or less semilunar periodicity, although phase differences occur both between and within species at different geographical locations, raising the possibility that tidal and diurnal cues are more important than semilunar cues in entraining the response. The ecological and evolutionary role(s) of synchronous spawning in the intertidal zone are considered, particularly with regard to hybridization/reproductive isolation in species complexes, and reproductive versus recruitment assurance in the intertidal zone, where synchronous spawning during calm periods may be important for recruitment assurance in addition to fertilization success. Ways in which the roles of spawning synchrony could be tested in closely related species with contrasting mating systems (outcrossing versus selfing) are discussed.'

input_data = {'abstract':abstract}
input_json = json.dumps(input_data)

input_fn_output = input_fn(input_json)
model = model_fn('../')
results = predict_fn(input_fn_output,model)
print(output_fn(results))