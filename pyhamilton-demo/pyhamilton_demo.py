"""Internal standard + patient sample prep on a 96-well deep-well plate.

Runs on a Hamilton STAR through pyhamilton:

1. Add 700 uL of internal standard (acetonitrile) from the center trough to
   every well. One set of 8 tips is pre-wetted, used for all 12 columns, then
   discarded.
2. Add 100 uL of patient sample from the glass tubes on 3 sample carriers
   (samples 1-96 go to wells A1-H12). Each batch of 8 uses new tips.
3. Mix each well 3 times (400 uL) right after the sample is dispensed.

Usage (from this folder, with the venv active):

    python pyhamilton_demo.py

VENUS Run Control opens. Press the green Play button to start the method.
Turn on Simulation mode in the VENUS System Configuration Editor for a dry run.

See pyhamilton_demo.ipynb for a step-by-step explanation of this procedure.
"""

import logging
from dataclasses import dataclass

from pyhamilton import (
    HamiltonInterface,
    LayoutManager,
    layout_item,
    Tip96,
    Plate96,
    Reservoir60mL,
    EppiCarrier32,
    initialize,
    tip_pick_up,
    aspirate,
    dispense,
    tip_eject,
    check_liquid_class_exists,
    copy_liquid_class,
    set_tip_type,
)

log = logging.getLogger(__name__)

# --- Deck layout ------------------------------------------------------------

LAYOUT_FILE = r"C:\Program Files (x86)\HAMILTON\Methods\Demo\msacl-2026-demo.lay"

# Labware names as they appear in the layout file
IS_TIPS = 'htf_l_0001'                     # 1000 uL filter tips, step 1
SAMPLE_TIPS = 'htf_l_0002'                 # 1000 uL filter tips, steps 2-3
TROUGH = 'rgt_cont_120ml_BC_A00_0002'      # center trough: internal standard
PLATE = 'Cos_96_DW_2mL_0001'               # 2 mL deep-well plate
SAMPLE_RACKS = (
    'SMP_CAR_32_13x100_A00_0001',          # samples 1-32
    'SMP_CAR_32_13x100_A00_0002',          # samples 33-64
    'SMP_CAR_32_13x100_A00_0003',          # samples 65-96
)

NUM_CHANNELS = 8
NUM_COLUMNS = 12
TUBES_PER_RACK = 32

# --- Volumes and mixing (uL) ------------------------------------------------

IS_VOLUME = 700
SAMPLE_VOLUME = 100
PREWET_CYCLES = 3   # pre-wet the IS tips before the first dispense
MIX_CYCLES = 3      # mix each well after adding the sample
MIX_VOLUME = 400    # half of the 800 uL in each well

# --- Liquid classes ---------------------------------------------------------

# Internal standard is in acetonitrile; jet dispense into empty wells.
IS_LIQUID_CLASS = 'HighVolumeFilter_Acetonitrile_DispenseJet_Empty'
# Built-in class that IS_LIQUID_CLASS is copied from (non-filter tips).
IS_SOURCE_LIQUID_CLASS = 'HighVolumeAcetonitrilDispenseJet_Empty'
# VENUS tip type for 1000 uL filter tips. pyhamilton's TipType enum has
# 4 and 5 swapped; 5 matches the built-in HighVolumeFilter_ classes.
FILTER_1000UL_TIP_TYPE = 5

# Samples are dilute urine; surface dispense into the 700 uL already in the well.
SAMPLE_LIQUID_CLASS = 'HighVolumeFilter_Water_DispenseSurface_Empty'


@dataclass
class Deck:
    """Labware objects looked up from the deck layout."""
    is_tips: Tip96
    sample_tips: Tip96
    trough: Reservoir60mL
    plate: Plate96
    sample_racks: list


def load_deck(layout_file):
    """Install the layout file and look up every piece of labware by name.

    Raises an error if a name is missing from the layout, before the robot moves.
    """
    lmgr = LayoutManager(layout_file)
    return Deck(
        is_tips=layout_item(lmgr, Tip96, IS_TIPS),
        sample_tips=layout_item(lmgr, Tip96, SAMPLE_TIPS),
        # No 120 mL trough class; Reservoir60mL has the same 8 positions.
        trough=layout_item(lmgr, Reservoir60mL, TROUGH),
        plate=layout_item(lmgr, Plate96, PLATE),
        # EppiCarrier32 works for any 32-position tube carrier.
        sample_racks=[layout_item(lmgr, EppiCarrier32, name) for name in SAMPLE_RACKS],
    )


def channel_positions(labware, first_index):
    """Return one (labware, index) position per channel, starting at first_index."""
    return [(labware, first_index + i) for i in range(NUM_CHANNELS)]


def ensure_is_liquid_class(ham_int):
    """Create the acetonitrile liquid class for filter tips if it doesn't exist yet."""
    if check_liquid_class_exists(IS_LIQUID_CLASS):
        log.info('Liquid class %s already exists', IS_LIQUID_CLASS)
        return
    copy_liquid_class(ham_int, IS_SOURCE_LIQUID_CLASS, IS_LIQUID_CLASS)
    set_tip_type(ham_int, IS_LIQUID_CLASS, FILTER_1000UL_TIP_TYPE)
    log.info('Created liquid class %s', IS_LIQUID_CLASS)


def add_internal_standard(ham_int, deck):
    """Step 1: add internal standard to all 12 columns with one set of tips."""
    trough_positions = channel_positions(deck.trough, 0)
    volumes = [IS_VOLUME] * NUM_CHANNELS

    tip_pick_up(ham_int, channel_positions(deck.is_tips, 0))

    for column in range(NUM_COLUMNS):
        log.info('Adding internal standard to column %d', column + 1)
        if column == 0:
            # Pre-wet the tips with acetonitrile on the first aspirate only
            aspirate(ham_int, trough_positions, volumes, liquidClass=IS_LIQUID_CLASS,
                     mixCycles=PREWET_CYCLES, mixVolume=IS_VOLUME)
        else:
            aspirate(ham_int, trough_positions, volumes, liquidClass=IS_LIQUID_CLASS)
        dispense(ham_int, channel_positions(deck.plate, column * NUM_CHANNELS), volumes,
                 liquidClass=IS_LIQUID_CLASS)

    tip_eject(ham_int)  # default waste


def add_samples_and_mix(ham_int, deck):
    """Steps 2 and 3: add each batch of 8 samples to one column and mix, with new tips."""
    volumes = [SAMPLE_VOLUME] * NUM_CHANNELS

    for batch in range(NUM_COLUMNS):
        first = batch * NUM_CHANNELS  # index of the first sample, tip and well
        rack = deck.sample_racks[first // TUBES_PER_RACK]
        first_tube = first % TUBES_PER_RACK

        log.info('Samples %d-%d -> column %d', first + 1, first + NUM_CHANNELS, batch + 1)
        tip_pick_up(ham_int, channel_positions(deck.sample_tips, first))
        aspirate(ham_int, channel_positions(rack, first_tube), volumes,
                 liquidClass=SAMPLE_LIQUID_CLASS)
        # Mixing happens after the dispense, in the full 800 uL
        dispense(ham_int, channel_positions(deck.plate, first), volumes,
                 liquidClass=SAMPLE_LIQUID_CLASS,
                 mixCycles=MIX_CYCLES, mixVolume=MIX_VOLUME)
        tip_eject(ham_int)


def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    deck = load_deck(LAYOUT_FILE)

    # The with block stops the interface (and Run Control) even if a step fails.
    with HamiltonInterface(windowed=True) as ham_int:
        initialize(ham_int)  # waits up to 300 s, so there is time to press Play
        ensure_is_liquid_class(ham_int)
        add_internal_standard(ham_int, deck)
        add_samples_and_mix(ham_int, deck)

    log.info('Run complete')


if __name__ == '__main__':
    main()
