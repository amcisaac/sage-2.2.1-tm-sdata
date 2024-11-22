import click
from collections import defaultdict
from copy import deepcopy

@click.command()
@click.option(
    "--output",
    "output_path",
    type=click.Path(exists=False, dir_okay=False, file_okay=True),
    required=True,
    help="The path to the output force field file.",
)
@click.option(
    "--force-field-name",
    type=str,
    default="openff_unconstrained-2.2.1.offxml",
    help="The name of the force field to download.",
    show_default=True,
)
def download_force_field(
    output_path: str,
    force_field_name: str = "openff_unconstrained-2.2.1.offxml",
):
    from openff.toolkit import ForceField
    from openff.units import unit

    force_field = ForceField(force_field_name)

    # Copied Brent's Torsion multiplicity workflow
    with open("to_add.dat") as inp:
        to_add = [
            line.strip()
            for line in inp
            if not line.startswith("#") and len(line) > 1
        ]

    new_params = defaultdict(list)
    for line in to_add:
        [pid, smirks] = line.split()
        new_params[pid].append(smirks)
    
    to_remove = ["t123"]
    
    torsions = force_field.get_parameter_handler("ProperTorsions")
    
    old = deepcopy(torsions.parameters)
    torsions.parameters.clear()
    
    for t in old:
        if t.id in new_params:
            for i, p in enumerate(new_params[t.id]):
                tmp = deepcopy(t)
                tmp.id = t.id + "ghijkl"[i]
                tmp.smirks = p
                torsions.parameters.append(tmp)
        elif t.id not in to_remove:
            torsions.parameters.append(t)



    # Write out file
    force_field.to_file(output_path)


if __name__ == "__main__":
    download_force_field()
