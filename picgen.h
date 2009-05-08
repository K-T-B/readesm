/* Copyright 2009 Andreas Gölzer

This file is part of readESM.

readESM is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

readESM is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with readESM.  If not, see <http://www.gnu.org/licenses/>. */

#ifndef PICGEN_H
#define PICGEN_H PICGEN_H
#include "typedefs.h"

class picgen : public ostringstream{
	public:
	virtual string str(){ return ostringstream::str(); }
	virtual void add(int from, int duration, int height, string color, string title) {}
};

void drawDayOutline(ostringstream& o){
	o << "<svg xmlns='http://www.w3.org/2000/svg' width='740' height='120'>" ;
	o << "<g transform='translate(10,0)'>";
	o << "<g style='text-anchor:middle;font-size:16px;'>";
	for(int j = 0; j < 25; ++j) o << "<text x='"<< (j * 30) << "' y='118'>" << j << "</text><line x1='" << (j * 30) << "' y1='100' x2='" << (j * 30) << "' y2='104' style='stroke-width:2;stroke:black' />";
	o << "</g>";
	o << "<polyline points='0,0 720,0 720,100 0,100 0,0' style='fill:none;stroke:black;stroke-width:2'/>";
}
const char* DayOutlineEnd = "</g></svg>";

class htmlBarGraph : public picgen {
	static const int compressh = 2;
	public:
	virtual void add(int from, int duration, int height, string color, string title) {
		(*this) << "<img src='images/" << color <<".gif' width='" << (duration / compressh) << "' height='" << height << "' title='" << title << "' alt='" << title << "'/>";
	}
	virtual string str(){
		ostringstream o;
		o << ostringstream::str() << "<img src='images/scale.gif' height='20' width='" << (1440 / compressh) << "' alt='scale' />";
		return o.str();
	}
};


class svgBarGraph : public picgen {
	public:
	virtual void add(int from, int duration, int height, string color, string title) {
		(*this) << "<rect x='" << from << "' fill='" << color <<"' width='" << duration << "' height='" << height << "' title='" << title << "' />";
	}
	virtual string str(){
		ostringstream o;
		drawDayOutline(o);
		o << "<g transform='scale(0.5,-1) translate(0,-100)'>" << ostringstream::str() << "</g>" << DayOutlineEnd;
		return o.str();
	}
};


class svgPlotGraph : public picgen {
	public:
	virtual void add(int from, int duration, int height, string color, string title) {
		(*this) << "<rect x='" << from << "' fill='" << color <<"' width='" << duration << "' height='" << height << "' title='" << title << "' />";
	}
	virtual string str(){
		ostringstream o;
		drawDayOutline(o);
		o << "<g transform='scale(0.0083333,-1) translate(0,-100)'><path style='stroke:#dd2200' d='M 0 0 L " << ostringstream::str() << "' /></g>" << DayOutlineEnd;
		return o.str();
	}
};

#endif
