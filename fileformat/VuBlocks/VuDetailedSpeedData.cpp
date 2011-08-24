#include "VuDetailedSpeedData.h"
#include "../PictureGenerators/SvgDayVelocity.h"

VuDetailedSpeedData::VuDetailedSpeedData(const constDataPointer& start) : RawVuDetailedSpeedData(start) {}

void VuDetailedSpeedData::printOn(reporter& report) const {
	if(!report.hasPlotGraph()) {
		RawVuDetailedSpeedData::printOn(report);
		return;
	}
	if(vuDetailedSpeedBlocks.size() < 1) return;
	
	SvgDayVelocity visualization;
	QDateTime daystart = QDateTime(vuDetailedSpeedBlocks[0].speedBlockBeginDate.date());
	int lastDifference = 0;
	for(uint j = 0; j < vuDetailedSpeedBlocks.size(); ++j) {
		int difference = daystart.secsTo(vuDetailedSpeedBlocks[j].speedBlockBeginDate);
		if(difference > 86400){
			visualization.add(lastDifference + 1, 0);
			report(daystart.date().toString(),visualization.toString());
			daystart = QDateTime(vuDetailedSpeedBlocks[j].speedBlockBeginDate.date());
			difference = daystart.secsTo(vuDetailedSpeedBlocks[j].speedBlockBeginDate);
			visualization.reset();
			lastDifference = 0;
		}
		if(difference > lastDifference + 60){
			visualization.add(lastDifference + 1, 0);
			visualization.add(difference - 1, 0);
		}
		for(int k = 0; k < 60; ++k)
			visualization.add(difference + k, vuDetailedSpeedBlocks[j].speedsPerSecond[k]);
		lastDifference = difference;
	}
	if(lastDifference != 0){
		visualization.add(lastDifference + 1, 0);
		report(daystart.date().toString(), visualization.toString());
	}
}
