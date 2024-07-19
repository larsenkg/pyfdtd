# pyfdtd is a simple 2d fdtd using numpy
# Copyright (C) 2012  Patrik Gebhardt
# Contact: grosser.knuff@googlemail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import json

from .field import Field
from .listener import Listener
from .material import Material
from .parser import BooleanParser, material_from_string, source_from_string
from .solver import Solver


class Job:
    def __init__(self):
        # create standart values
        self.config = {"size": (0.4, 0.4), "delta": (0.001, 0.001), "duration": 5e-9}
        self.listener = []
        self.source = []
        self.material = {"electric": [], "magnetic": []}

    def load(self, fname):
        # open file
        f = open(fname, "rb")

        # unjson
        indict = json.load(f)

        # extract file
        self.config = indict["config"]
        self.material = indict["material"]
        self.source = indict["source"]
        self.listener = indict["listener"]

        # close file
        f.close()

        # return self for chaining
        return self

    def save(self, fname):
        # open file
        f = open(fname, "wb")

        # put everything in one dict
        outdict = {
            "config": self.config,
            "material": self.material,
            "source": self.source,
            "listener": self.listener,
        }

        # json
        json.dump(outdict, f, sort_keys=True, indent=4)

        # close file
        f.close()

        # return self for chaining
        return self

    def get_solver(self):
        # create empty solver
        solver = Solver(Field(self.config["size"], self.config["delta"]))

        # create parser
        parser = BooleanParser()

        # get meshgrid
        x, y = solver.material["electric"].meshgrid

        # create materials
        for name, mask, function in self.material["electric"]:
            solver.material["electric"][parser.parse(str(mask), x=x, y=y)] = (
                material_from_string(function, {"epsilon": Material.epsilon})
            )

        for name, mask, function in self.material["magnetic"]:
            solver.material["magnetic"][parser.parse(str(mask), x=x, y=y)] = (
                material_from_string(function, {"mu": Material.mu})
            )

        # create source
        for name, mask, function in self.source:
            solver.source[parser.parse(str(mask), x=x, y=y)] = source_from_string(
                function
            )

        # create listener
        for name, x, y in self.listener:
            solver.listener.append(Listener(x, y))

        # return new solver
        return solver
