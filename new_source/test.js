let entity, entityName, entityIdString, selectedSensor, isActive, tempValue, humValue, aqi, aqiTime, aqiDate, pm25AqiValue, pm10AqiValue, no2AqiValue, coAqiValue, so2AqiValue, o3AqiValue;
if (data && data.length) {
  selectedSensor = data[1];
  entity = data[1] ? data[1] : data[0];
  entityIdString = '{entityType: '+ (entity['entityType'] === 'ASSET' ? '\'ASSET\'' : '\'DEVICE\'') +', id: \''+ entity['entityId'] + '\'}';
  entityName = entity.entityLabel ? entity.entityLabel : entity.entityName;
  tempValue = processValue(entity['temperature'], 0);
  humValue = processValue(entity['humidity'], 0);
  aqi = processValue(entity['aqi'], 0);
  isActive = true;

  if (selectedSensor) {
    pm25AqiValue = processValue(entity['pm25Aqi'], 3);
    pm10AqiValue = processValue(entity['pm10Aqi'], 3);
    no2AqiValue = processValue(entity['no2Aqi'], 3);
    coAqiValue = processValue(entity['coAqi'], 3);
    so2AqiValue = processValue(entity['so2Aqi'], 3);
    o3AqiValue = processValue(entity['o3Aqi'], 3);


    no2Aqi24Value = processValue(entity['NO2_24h'], 3);
    coAqi24Value = processValue(entity['CO_24h'], 3);
    so2Aqi24Value = processValue(entity['SO2_24h'], 3);
    o3Aqi24Value = processValue(entity['O3_24h'], 3);
    pm25Aqi24Value = processValue(entity['PM25_24h'], 3);
    pm10Aqi24Value = processValue(entity['PM10_24h'], 3);

    no2Aqi48Value = processValue(entity['NO2_48h'], 3);
    coAqi48Value = processValue(entity['CO_48h'], 3);
    so2Aqi48Value = processValue(entity['SO2_48h'], 3);
    o3Aqi48Value = processValue(entity['O3_48h'], 3);
    pm2548hoursAqi48Value = processValue(entity['PM25_48h'], 3);
    pm1048hoursAqi48Value = processValue(entity['PM10_48h'], 3);

    no2Aqi72Value = processValue(entity['NO2_72h'], 3);
    coAqi72Value = processValue(entity['CO_72h'], 3);
    so2Aqi72Value = processValue(entity['SO2_72h'], 3);
    o3Aqi72Value = processValue(entity['O3_72h'], 3);
    pm25Aqi72Value = processValue(entity['PM25_72h'], 3);
    pm10Aqi72Value = processValue(entity['PM10_72h'], 3);

    isActive = entity['active'] === 'true';
  }

  if (!!(entity['aqi|ts'])) {
    const isCurrentDay = moment(entity['aqi|ts']).isSame(new Date(), 'day');
    aqiTime = isCurrentDay ? moment(entity['aqi|ts']).format('HH:mm') : moment(entity['aqi|ts']).fromNow();
    aqiDate = moment(entity['aqi|ts']).format('D MMM YYYY HH:mm');
  } else {
    aqiTime = 'N/A';
    aqiDate = 'N/A';
  }
} else {
  entityName = 'N/A';
  tempValue = 'N/A';
  humValue = 'N/A';
  aqi = 'N/A';
  aqiTime = 'N/A';
  aqiDate = 'N/A';
  pm25AqiValue = 'N/A';
  pm10AqiValue = 'N/A';
  no2AqiValue = 'N/A';
  coAqiValue = 'N/A';
  so2AqiValue = 'N/A';
  o3AqiValue = 'N/A';
}

const legend = [
  {
    range: [0, 50],
    colors: [[128, 186, 60], [176, 214, 72]],
    inactiveColors: [[226, 226, 226], [215, 215, 215]],
    icon: 'check_circle',
    shortStatus: 'CLEAN',
    status: {
      header: 'Air is clean',
      desc: 'It\'s worth taking a walk or airing out the room.'
    }
  },
  {
    range: [50, 100],
    colors: [[176, 214, 72], [245, 189, 51]],
    inactiveColors: [[215, 215, 215], [195, 195, 195]],
    icon: 'check_circle',
    shortStatus: 'CLEAN',
    status: {
      header: 'Air is moderately clean',
      desc: 'Unusually sensitive individuals should consider limiting prolonged exertion especially near busy roads.'
    }
  },
  {
    range: [100, 150],
    colors: [[245, 189, 51], [235, 117, 51]],
    inactiveColors: [[195, 195, 195], [160, 160, 160]],
    icon: 'error',
    shortStatus: 'UNHEALTHY',
    status: {
      header: 'Air is unhealthy for sensitive groups',
      desc: 'People with asthma, children and older adults should limit prolonged exertion especially near busy roads.'
    }
  },
  {
    range: [150, 200],
    colors: [[235, 117, 51], [248, 76, 57]],
    inactiveColors: [[160, 160, 160], [136, 136, 136]],
    icon: 'error',
    shortStatus: 'UNHEALTHY',
    status: {
      header: 'Air is unhealthy',
      desc: 'People with asthma, children and older adults should avoid prolonged exertion near roadways; everyone else should reduce outdoor exertion.'
    }
  },
  {
    range: [200, 300],
    colors: [[248, 76, 57], [188, 52, 53]],
    inactiveColors: [[136, 136, 136], [119, 119, 119]],
    icon: 'error',
    shortStatus: 'VERY UNHEALTHY',
    status: {
      header: 'Air is very unhealthy',
      desc: 'People with asthma, children and older adults should avoid all outdoor exertion; everyone else should avoid prolonged exertion especially near busy roads.'
    }
  },
  {
    range: [300],
    colors: [[188, 52, 53], [128, 27, 49]],
    inactiveColors: [[119, 119, 119], [78, 78, 78]],
    icon: 'error',
    shortStatus: 'HAZARDOUS',
    status: {
      header: 'Air is hazardous',
      desc: 'Everyone should avoid all outdoor exertion.'
    }
  }
];

const targetSegment = getLegendSegment(aqi);
const aqiColor = getAqiColor(aqi);

const tempSvg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">' +
  '<path d="M16 4.7251C16 4.31088 16.3358 3.9751 16.75 3.9751H17.25C17.6642 3.9751 18 4.31088 18 4.7251C18 5.13931 17.6642 5.4751 17.25 5.4751H16.75C16.3358 5.4751 16 5.13931 16 4.7251ZM16 7.7251C16 7.31088 16.3358 6.9751 16.75 6.9751H19.25C19.6642 6.9751 20 7.31088 20 7.7251C20 8.13931 19.6642 8.4751 19.25 8.4751H16.75C16.3358 8.4751 16 8.13931 16 7.7251ZM16 10.7251C16 10.3109 16.3358 9.9751 16.75 9.9751H17.25C17.6642 9.9751 18 10.3109 18 10.7251C18 11.1393 17.6642 11.4751 17.25 11.4751H16.75C16.3358 11.4751 16 11.1393 16 10.7251Z" fill="#9FA6B4"/>' +
  '<path fill-rule="evenodd" clip-rule="evenodd" d="M7.00037 13.5957L7.5 13.1485V12.478V6C7.5 4.61929 8.61929 3.5 10 3.5C11.3807 3.5 12.5 4.61929 12.5 6V12.478V13.1485L12.9996 13.5957C13.9227 14.4218 14.5 15.6176 14.5 16.9502C14.5 19.4355 12.4853 21.4502 10 21.4502C7.51472 21.4502 5.5 19.4355 5.5 16.9502C5.5 15.6176 6.07735 14.4218 7.00037 13.5957ZM10 2C7.79086 2 6 3.79086 6 6V12.478C4.7725 13.5766 4 15.1732 4 16.9502C4 20.2639 6.68629 22.9502 10 22.9502C13.3137 22.9502 16 20.2639 16 16.9502C16 15.1732 15.2275 13.5766 14 12.478V6C14 3.79086 12.2091 2 10 2ZM9.25 9.2C9.25 8.78579 9.58579 8.45 10 8.45C10.4142 8.45 10.75 8.78579 10.75 9.2V14.5645C11.7643 14.883 12.5 15.8306 12.5 16.95C12.5 18.3307 11.3807 19.45 10 19.45C8.61929 19.45 7.5 18.3307 7.5 16.95C7.5 15.8306 8.23572 14.883 9.25 14.5645V9.2Z" fill="#9FA6B4"/>' +
  '</svg>';
const encodedTempSvg = encodeURIComponent(tempSvg);
const tempSvgUrl = 'data:image/svg+xml,' + encodedTempSvg;

const humSvg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">' +
  '<path fill-rule="evenodd" clip-rule="evenodd" d="M8.72245 8.04817L11.9901 4.50233L11.9909 4.50199C11.9954 4.50036 11.9987 4.5 12.001 4.5C12.0033 4.5 12.0065 4.50034 12.0109 4.50195C12.0152 4.50351 12.0231 4.50711 12.0336 4.51576C12.6326 5.00891 14.0389 6.53246 15.3324 7.98091C15.4531 8.11605 15.574 8.25034 15.6945 8.38413C16.3748 9.13973 17.041 9.87969 17.5745 10.6708C18.1953 11.5913 18.5801 12.5041 18.5801 13.4682C18.5801 17.3939 15.5925 20.4988 12 20.4988C8.40745 20.4988 5.41992 17.3939 5.41992 13.4682C5.41992 12.5121 5.8102 11.6097 6.44219 10.6999C6.98429 9.9195 7.66039 9.19205 8.35029 8.44974L8.35029 8.44974L8.35043 8.44959C8.47422 8.31639 8.59846 8.18271 8.72245 8.04817ZM12.9869 3.35769C12.4065 2.8799 11.5919 2.88101 11.0127 3.35958L10.9734 3.39204L10.9389 3.42952L7.6194 7.03167C7.50481 7.15601 7.38679 7.28286 7.26653 7.41212C6.57916 8.15088 5.81876 8.96814 5.21026 9.84412C4.48788 10.884 3.91992 12.086 3.91992 13.4682C3.91992 18.1367 7.49596 21.9988 12 21.9988C16.504 21.9988 20.0801 18.1367 20.0801 13.4682C20.0801 12.0888 19.5262 10.8821 18.8181 9.83209C18.2205 8.94595 17.473 8.11654 16.7954 7.36475L16.7951 7.36447C16.678 7.23455 16.563 7.10696 16.4512 6.98179C15.1933 5.57318 13.6968 3.94208 12.9869 3.35769ZM16.7862 13.5273C16.7862 13.1131 16.4504 12.7773 16.0362 12.7773C15.622 12.7773 15.2862 13.1131 15.2862 13.5273C15.2862 13.8383 15.212 14.3898 14.9813 14.9373C14.7525 15.4804 14.3955 15.962 13.866 16.243C13.5002 16.4372 13.361 16.8912 13.5552 17.2571C13.7493 17.6229 14.2034 17.7621 14.5692 17.5679C15.4946 17.0768 16.0469 16.2715 16.3636 15.5197C16.6785 14.7722 16.7862 14.0207 16.7862 13.5273Z" fill="#9FA6B4"/>' +
  '</svg>';
const encodedHumSvg = encodeURIComponent(humSvg);
const humSvgUrl = 'data:image/svg+xml,' + encodedHumSvg;

const header =  '<div class="header flex flex-col">' +
  '<div class="flex flex-1 flex-row items-center justify-between" style="margin-bottom:4px">' +
  '<div class="entity-name flex flex-row">'+
  (selectedSensor ? '<button id="go-back" mat-icon-button matTooltip="Go back" class="go-back-bttn" aria-label="Go back">' +
    '<mat-icon class="tb-mat-20">arrow_back</mat-icon>' +
    '</button>' : '') +
  '<span>' + entityName + '</span>' +
  '</div>' +
  '<div class="aqi-status" style="background-color:'+ (isActive ? aqiColor : '#B4B4B4') +'">'+ getShortStatus() +'</div>' +
  '</div>' +
  '<div class="flex flex-1 flex-row items-center justify-between">' +
  '<div class="flex flex-row items-center justify-start">' +
//   '<img style="vertical-align: middle;" class="title-icon mat-icon" src="'+ tempSvgUrl +'">' +
//   '<div class="telemetry-value" style="margin-right:12px">'+ tempValue +'°C</div>' +
//   '<img style="vertical-align: middle;" class="title-icon mat-icon" src="'+ humSvgUrl +'">' +
  '<div class="telemetry-value">'+ '</div>' +
  '</div>' +
  '<div class="last-ts '+ (isActive ? '' : 'last-ts-inactive') +'" matTooltip="'+ aqiDate +'" matTooltipPosition="right">last update: '+ aqiTime +'</div>' +
  '</div>' +
  '</div>';

const mainPart = '<div class="main-part flex flex-col items-center justify-start">' +
  '<div class="aqi-value">'+ aqi +'</div>' +
  '<div class="aqi-label flex flex-row">' +
  'US AQI' +
  '<button id="aqi-desc" mat-icon-button class="aqi-info-bttn" aria-label="What is US AQI">' +
  '<mat-icon class="tb-mat-20">info_outline</mat-icon>' +
  '</button>' +
  '</div>' +
  '<div class="legend-scale-continer flex flex-col">' +
  '<div class="legend-scale-pointer" style="'+ getScalePointerPosition(aqi) +';border-top:8px solid '+ aqiColor +';"></div>' +
  '<div class="legend-scale '+ (isActive ? '' : 'legend-scale-inactive') +'"></div>' +
  '<div class="scale-ticks flex flex-row items-center justify-between">' +
  '<div class="tick"><div class="tick-value">0</div></div>' +
  '<div class="tick"><div class="tick-value">50</div></div>' +
  '<div class="tick"><div class="tick-value">100</div></div>' +
  '<div class="tick"><div class="tick-value">150</div></div>' +
  '<div class="tick"><div class="tick-value">200</div></div>' +
  '<div class="tick"><div class="tick-value">300</div></div>' +
  '<div class="tick"><div class="tick-value">>301</div></div>' +
  '</div>' +
  '</div>' +
  '</div>';

const statusDescription = '<div class="status-desc-container flex flex-row">' +
  '<div class="icon-status" style="line-height:initial">' +
  '<mat-icon class="tb-mat-18" style="color:'+ aqiColor +'">'+ (targetSegment ? targetSegment.icon : 'check_circle') +'</mat-icon>' +
  '</div>' +
  '<div class="status-desc flex flex-col">' +
  '<div class="status-header">' + (targetSegment ? targetSegment.status.header : 'Air is clean') + '</div>' +
  '<div class="desc">' + (targetSegment ? targetSegment.status.desc : 'It\'s worth taking a walk or airing out the room.') + '</div>' +
  '</div>' +
  '</div>';

const inactiveStatusDescription = '<div class="status-desc-container status-desc-container-inactive flex flex-row">' +
  '<div class="icon-status" style="line-height:initial">' +
  '<mat-icon class="tb-mat-18" style="color:#fff">error</mat-icon>' +
  '</div>' +
  '<div class="status-desc flex flex-col">' +
  '<div class="status-header">Data is outdated</div>' +
  '<div class="desc">The sensor doesn’t work, but we’re already repairing it.</div>' +
  '</div>' +
  '</div>';

const aqiComponentsSection = (!selectedSensor ? '' :
  '<div class="components-container flex flex-col">' +
  '<div class="last-ts '+ (isActive ? '' : 'last-ts-inactive') +'" matTooltip="'+ aqiDate +'" matTooltipPosition="right" style="font-size: 14px; font-weight: bold;">'+ 'Current Data' +'</div>' +
  '<mat-button-toggle-group class="aqi-components flex flex-row flex-wrap" name="aqiСomponents">' +
  '<mat-button-toggle id="pm25" class="aqi-component flex-full" style="margin-right:6px; max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name" style="line-height:25px">PM2.5</div>' +
  '<div class="aqi-component-value">'+ pm25AqiValue +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(pm25AqiValue) + ';width:' + getAqiComponentBarWidth(pm25AqiValue) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="pm10" class="aqi-component flex-full" style="margin-left:3px;margin-right:3px;max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name" style="line-height:25px">PM10</div>' +
  '<div class="aqi-component-value">'+ pm10AqiValue +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(pm10AqiValue) + ';width:' + getAqiComponentBarWidth(pm10AqiValue) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="no2" class="aqi-component flex-full" style="margin-left:6px;max-width:calc(33.33% - 6px);">'+
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name">NO<sub>2</sub></div>' +
  '<div class="aqi-component-value">'+ no2AqiValue +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(no2AqiValue) + ';width:' + getAqiComponentBarWidth(no2AqiValue) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="co" class="aqi-component flex-full" style="margin-right:6px;max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name" style="line-height:25px">CO</div>' +
  '<div class="aqi-component-value">'+ coAqiValue +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(coAqiValue) + ';width:' + getAqiComponentBarWidth(coAqiValue) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="so2" class="aqi-component flex-full" style="margin-left:3px;margin-right:3px;max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name">SO<sub>2</sub></div>' +
  '<div class="aqi-component-value">'+ so2AqiValue +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(so2AqiValue) + ';width:' + getAqiComponentBarWidth(so2AqiValue) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="o3" class="aqi-component flex-full" style="margin-left:6px;max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name">O<sub>3</sub></div>' +
  '<div class="aqi-component-value">'+ o3AqiValue +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(o3AqiValue) + ';width:' + getAqiComponentBarWidth(o3AqiValue) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '</mat-button-toggle-group>' +
  '</div>');

const aqiComponents24ForeCastSection = (!selectedSensor ? '' :
  '<div class="components-container flex flex-col">' +
  '<div class="last-ts '+ (isActive ? '' : 'last-ts-inactive') +'" matTooltip="'+ aqiDate +'" matTooltipPosition="right" style="font-size: 14px; font-weight: bold; border-top: 1px solid #ddd; padding-top: 10px; margin-top: 10px;">' + 'Forecast in 24 hours' + '</div>' +
  '<mat-button-toggle-group class="aqi-components flex flex-row flex-wrap" name="aqiСomponents">' +
  '<mat-button-toggle id="pm25" class="aqi-component flex-full" style="margin-right:6px; max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name" style="line-height:25px">PM2.5</div>' +
  '<div class="aqi-component-value">'+ pm25Aqi24Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(pm25Aqi24Value) + ';width:' + getAqiComponentBarWidth(pm25Aqi24Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="pm10" class="aqi-component flex-full" style="margin-left:3px;margin-right:3px;max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name" style="line-height:25px">PM10</div>' +
  '<div class="aqi-component-value">'+ pm10Aqi24Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(pm10Aqi24Value) + ';width:' + getAqiComponentBarWidth(pm10Aqi24Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="no2" class="aqi-component flex-full" style="margin-left:6px;max-width:calc(33.33% - 6px);">'+
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name">NO<sub>2</sub></div>' +
  '<div class="aqi-component-value">'+ no2Aqi24Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(no2Aqi24Value) + ';width:' + getAqiComponentBarWidth(no2Aqi24Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="co" class="aqi-component flex-full" style="margin-right:6px;max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name" style="line-height:25px">CO</div>' +
  '<div class="aqi-component-value">'+ coAqi24Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(coAqi24Value) + ';width:' + getAqiComponentBarWidth(coAqi24Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="so2" class="aqi-component flex-full" style="margin-left:3px;margin-right:3px;max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name">SO<sub>2</sub></div>' +
  '<div class="aqi-component-value">'+ so2Aqi24Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(so2Aqi24Value) + ';width:' + getAqiComponentBarWidth(so2Aqi24Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="o3" class="aqi-component flex-full" style="margin-left:6px;max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name">O<sub>3</sub></div>' +
  '<div class="aqi-component-value">'+ o3Aqi24Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(o3Aqi24Value) + ';width:' + getAqiComponentBarWidth(o3Aqi24Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '</mat-button-toggle-group>' +
  '</div>');

const aqiComponents48ForeCastSection = (!selectedSensor ? '' :
  '<div class="components-container flex flex-col">' +
  '<div class="last-ts '+ (isActive ? '' : 'last-ts-inactive') +'" matTooltip="'+ aqiDate +'" matTooltipPosition="right" style="font-size: 14px; font-weight: bold; border-top: 1px solid #ddd; padding-top: 10px; margin-top: 10px;">' + 'Forecast in 48 hours' + '</div>' +
  '<mat-button-toggle-group class="aqi-components flex flex-row flex-wrap" name="aqiСomponents">' +
  '<mat-button-toggle id="pm25" class="aqi-component flex-full" style="margin-right:6px; max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name" style="line-height:25px">PM2.5</div>' +
  '<div class="aqi-component-value">'+ pm2548hoursAqi48Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(pm2548hoursAqi48Value) + ';width:' + getAqiComponentBarWidth(pm2548hoursAqi48Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="pm10" class="aqi-component flex-full" style="margin-left:3px;margin-right:3px;max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name" style="line-height:25px">PM10</div>' +
  '<div class="aqi-component-value">'+ pm1048hoursAqi48Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(pm1048hoursAqi48Value) + ';width:' + getAqiComponentBarWidth(pm1048hoursAqi48Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="no2" class="aqi-component flex-full" style="margin-left:6px;max-width:calc(33.33% - 6px);">'+
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name">NO<sub>2</sub></div>' +
  '<div class="aqi-component-value">'+ no2Aqi48Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(no2Aqi48Value) + ';width:' + getAqiComponentBarWidth(no2Aqi48Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="co" class="aqi-component flex-full" style="margin-right:6px;max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name" style="line-height:25px">CO</div>' +
  '<div class="aqi-component-value">'+ coAqi48Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(coAqi48Value) + ';width:' + getAqiComponentBarWidth(coAqi48Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="so2" class="aqi-component flex-full" style="margin-left:3px;margin-right:3px;max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name">SO<sub>2</sub></div>' +
  '<div class="aqi-component-value">'+ so2Aqi48Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(so2Aqi48Value) + ';width:' + getAqiComponentBarWidth(so2Aqi48Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="o3" class="aqi-component flex-full" style="margin-left:6px;max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name">O<sub>3</sub></div>' +
  '<div class="aqi-component-value">'+ o3Aqi48Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(o3Aqi48Value) + ';width:' + getAqiComponentBarWidth(o3Aqi48Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '</mat-button-toggle-group>' +
  '</div>');

const aqiComponents72ForeCastSection = (!selectedSensor ? '' :
  '<div class="components-container flex flex-col">' +
  '<div class="last-ts '+ (isActive ? '' : 'last-ts-inactive') +'" matTooltip="'+ aqiDate +'" matTooltipPosition="right" style="font-size: 14px; font-weight: bold; border-top: 1px solid #ddd; padding-top: 10px; margin-top: 10px;">' + 'Forecast in 72 hours' + '</div>' +
  '<mat-button-toggle-group class="aqi-components flex flex-row flex-wrap" name="aqiСomponents">' +
  '<mat-button-toggle id="pm25" class="aqi-component flex-full" style="margin-right:6px; max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name" style="line-height:25px">PM2.5</div>' +
  '<div class="aqi-component-value">'+ pm25Aqi72Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(pm25Aqi72Value) + ';width:' + getAqiComponentBarWidth(pm25Aqi72Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="pm10" class="aqi-component flex-full" style="margin-left:3px;margin-right:3px;max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name" style="line-height:25px">PM10</div>' +
  '<div class="aqi-component-value">'+ pm10Aqi72Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(pm10Aqi72Value) + ';width:' + getAqiComponentBarWidth(pm10Aqi72Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="no2" class="aqi-component flex-full" style="margin-left:6px;max-width:calc(33.33% - 6px);">'+
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name">NO<sub>2</sub></div>' +
  '<div class="aqi-component-value">'+ no2Aqi72Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(no2Aqi72Value) + ';width:' + getAqiComponentBarWidth(no2Aqi72Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="co" class="aqi-component flex-full" style="margin-right:6px;max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name" style="line-height:25px">CO</div>' +
  '<div class="aqi-component-value">'+ coAqi72Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(coAqi72Value) + ';width:' + getAqiComponentBarWidth(coAqi72Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="so2" class="aqi-component flex-full" style="margin-left:3px;margin-right:3px;max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name">SO<sub>2</sub></div>' +
  '<div class="aqi-component-value">'+ so2Aqi72Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(so2Aqi72Value) + ';width:' + getAqiComponentBarWidth(so2Aqi72Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '<mat-button-toggle id="o3" class="aqi-component flex-full" style="margin-left:6px;max-width:calc(33.33% - 6px);">' +
  '<div class="aqi-component-content flex flex-col items-start justify-between">' +
  '<div class="aqi-component-name">O<sub>3</sub></div>' +
  '<div class="aqi-component-value">'+ o3Aqi72Value +'</div>' +
  '<div class="aqi-component-bar">' +
  '<div class="aqi-component-bar-value" style="background-color:'+ getAqiColor(o3Aqi72Value) + ';width:' + getAqiComponentBarWidth(o3Aqi72Value) +'%"></div>' +
  '</div>' +
  '</div>' +
  '</mat-button-toggle>' +
  '</mat-button-toggle-group>' +
  '</div>');

return  '<div class="main-layout flex flex-col">' +
    header +
    mainPart +
    (isActive ? statusDescription : inactiveStatusDescription) +
    aqiComponentsSection +
    aqiComponents24ForeCastSection +
    aqiComponents48ForeCastSection +
    aqiComponents72ForeCastSection +
  '</div>';


function getLegendSegment(value) {
  if (value === 'N/A') {
    return null;
  }
  for (let i = 0; i < legend.length; i++) {
    if (i === 0 && value <= 0) {
      return legend[0];
    }
    if (i === legend.length - 1 && value > 300) {
      return legend[legend.length - 1];
    }
    if (value > legend[i].range[0] && value <= legend[i].range[1]) {
      return legend[i];
    }
  }
}

function getAqiColor(value) {
  const targetSegment = getLegendSegment(value);
  if (targetSegment) {
    if (targetSegment.range.length === 1) {
      return isActive ? 'rgb(128,27,49)' : 'rgb(78, 78, 78)';
    } else if (value < 0) {
      return isActive ? 'rgb(128,186,60)' : 'rgb(226, 226, 226)';
    } else {
      let ratio1 = (value - targetSegment.range[0]) / ((targetSegment.range[1] + 1) - targetSegment.range[0]);
      let ratio2 = 1 - ratio1;
      let colors = targetSegment[isActive ? 'colors' : 'inactiveColors'];
      return 'rgb(' + (Math.round(colors[0][0] * ratio2 + colors[1][0] * ratio1)) + ', '
        + (Math.round(colors[0][1] * ratio2 + colors[1][1] * ratio1)) + ', '
        + (Math.round(colors[0][2] * ratio2 + colors[1][2] * ratio1)) + ')';
    }
  } else {
    return 'rgb(180,180,180)';
  }
}

function getShortStatus() {
  if (isActive) {
    return targetSegment ? targetSegment.shortStatus : 'INACTIVE';
  } else {
    return 'INACTIVE';
  }
}

function getScalePointerPosition(value) {
  if (targetSegment) {
    if (targetSegment.range.length === 1) {
      return 'right:0;left:initial';
    } else if (value < 0) {
      return 'left:-4px';
    } else if (value >= 0 && value <= 200) {
      let ratio = parseFloat((100*value/300).toFixed(2));
      return 'left:calc('+ ratio + '% - 4px)';
    } else {
      let ratio = parseFloat((100*(value + 200)/600).toFixed(2));
      return 'left:calc('+ ratio + '% - 4px)';
    }
  } else {
    return 'left:-4px';
  }
}

function getAqiComponentBarWidth(value) {
  const targetSegment = getLegendSegment(value);
  if (targetSegment) {
    if (targetSegment.range.length === 1) {
      return '100';
    } else if (value < 0) {
      return '0';
    } else if (value >= 0 && value <= 200) {
      return parseFloat((100*value/300).toFixed(2));
    } else {
      return parseFloat((100*(value + 200)/600).toFixed(2));
    }
  } else {
    return '0';
  }
}

function isNumber(value) {
  return (typeof value === 'number' && isFinite(value));
}

function processValue(value, dec) {
  value = parseFloat(value);
  if (isNumber(value)) {
    if (isNumber(dec)) {
      value = parseFloat(value.toFixed(dec));
    }
    return value;
  } else {
    return 'N/A';
  }
}