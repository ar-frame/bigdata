
import { createChart, ColorType, MismatchDirection } from 'lightweight-charts';
import * as  LightweightCharts from 'lightweight-charts';
import React, { useEffect, useRef, useState } from 'react';

import Func from './tools/Func'

// 程序框架执行完成
let initok = false
let globalData = {}
let ACCOUNT_NAME = ''
let TIMEIDS = []
let allmarks = []
let maxLength = 3600 * 24 * 2
let startshowLength = maxLength - 3600 * 24 * 1

function ifDataLoadOk() {
    if (Object.keys(globalData).length > 0) {
        return true
    } else {
        return false
    }
}

export const ChartComponent = props => {
    const [title, setTitle] = useState('')
    // 数据加载完成
    const [loadok, setloadstate] = useState(false)
    const [tradedetails, setTradedetails] = useState('')
    const [stockdetails, setStockdetails] = useState('')
    const chartContainerRef = useRef()

    useEffect(
        () => {
            console.log('in shipan uef...', initok)
            const search = window.location.search
            const params = new URLSearchParams(search)
            ACCOUNT_NAME = params.get("account")
            console.log('ACCOUNT_NAME:', ACCOUNT_NAME)
            document.title = ACCOUNT_NAME + '实盘'
            const handleResize = () => {
                chart.applyOptions({ width: chartContainerRef.current.clientWidth })
            }

            // Get the current users primary locale
            const currentLocale = window.navigator.languages[0];
            // Create a number format using Intl.NumberFormat
            //   const myPriceFormatter = Intl.NumberFormat(currentLocale, {
            //         style: "currency",
            //         currency: "EUR", // Currency for data points
            //       }).format;

            const myPriceFormatter = p => {
                if (p > 0) {
                    if (p > 1000) {
                        p = p.toFixed(2)
                    } else if (p > 10) {
                        p = p.toFixed(3)
                    } else if (p > 1) {
                        p = p.toFixed(4)
                    } else {
                        p = p.toFixed(5)
                    }
                } else {
                    p = p.toFixed(2)
                }

                return p
            }

            const chart = createChart(chartContainerRef.current, {
                layout: {
                    background: { type: ColorType.Solid, color: 'white' },
                    textColor: 'black',
                },
                width: chartContainerRef.current.clientWidth,
                height: 700,
                // precision:3,
                localization: {
                    priceFormatter: myPriceFormatter,
                },
            });


            chart.applyOptions({
                watermark: {
                    visible: true,
                    fontSize: 12,
                    horzAlign: 'left',
                    vertAlign: 'bottom',
                    color: 'rgba(171, 71, 188, 0.6)',
                    text: 'KT量化',
                },
            });

            chart.subscribeCrosshairMove(param => {
                if (
                    param.point === undefined ||
                    !param.time ||
                    param.point.x < 0 ||
                    param.point.x > container.clientWidth ||
                    param.point.y < 0 ||
                    param.point.y > container.clientHeight
                ) {
                    toolTip.style.display = 'none';
                } else {
                    // time will be in the same format that we supplied to setData.
                    // thus it will be YYYY-MM-DD

                    const mstime = param.time * 1000
                    // const dateStr = new Date(mstime).toLocaleDateString() + " " + new Date(mstime).toTimeString().split(' ')[0]
                    let dateStr = ''


                    let rowdata = globalData['data'][param.logical]
                    if (rowdata && 'extra' in rowdata) {
                        let extra = rowdata['extra']
                        dateStr = extra['showtime']

                        if ('tradeopt' in extra) {
                            let tradeopt = extra['tradeopt']
                            let indi = extra['name']
                            dateStr = dateStr + "<br>\n<b>" + tradeopt + "</b>\n(" + indi + ")@" + extra[indi]
                        }
                    }

                    // console.log(param.logical, globalData)
                    let stginfo = globalData['stginfo']
                    toolTip.style.display = 'block';
                    // console.log('param:', param)
                    const data = param.seriesData.get(candleSeries);
                    // console.log('data:', data)
                    const price = data.value !== undefined ? data.value : data.close;
                    // const price = 100;
                    toolTip.innerHTML = `<div style="color: ${'rgba( 239, 83, 80, 1)'}">${stginfo['variety']}</div><div style="font-size: 24px; margin: 4px 0px; color: ${'black'}">
        ${Math.round(10000 * price) / 10000}
        </div><div style="color: ${'black'}">
        ${dateStr}
        </div>`;

                    let left = param.point.x; // relative to timeScale
                    const timeScaleWidth = chart.timeScale().width();
                    const priceScaleWidth = chart.priceScale('left').width();
                    const halfTooltipWidth = toolTipWidth / 2;
                    left += priceScaleWidth - halfTooltipWidth;
                    left = Math.min(left, priceScaleWidth + timeScaleWidth - toolTipWidth);
                    left = Math.max(left, priceScaleWidth);

                    toolTip.style.left = left + 'px';
                    // toolTip.style.top = 0 + 'px';
                }
            });

            chart.timeScale().applyOptions({ barSpacing: 1, minBarSpacing:0.001 })
            chart.timeScale().fitContent()

            const indiSeries = chart.addLineSeries({
                title: '指标',
                color: '#170ae3',
                lineWidth: 1,
                // disabling built-in price lines
                lastValueVisible: false,
                priceLineVisible: false,
                pane: 1,
            })

            const moneySeries = chart.addLineSeries({
                title: '资金',
                color: '#0062CC',
                lineWidth: 1,
                // disabling built-in price lines
                lastValueVisible: false,
                priceLineVisible: false,
                pane: 2,
                height: 20
            })

            const profitSeries = chart.addLineSeries({
                title: '利润',
                color: '#e15b1b',
                lineWidth: 1,
                // disabling built-in price lines
                // lastValueVisible: false,
                // priceLineVisible: false,
                pane: 3,
            })
            const candleSeries = chart.addCandlestickSeries({
                upColor: 'red',
                downColor: 'green',
                borderVisible: false,
                precision: 3,
            });
            const volumeSeries = chart.addHistogramSeries({
                secondary: 'volume',
                priceScaleId: '',
                pane: 0
            });
            volumeSeries.priceScale().applyOptions({
                // set the positioning of the volume series
                scaleMargins: {
                    top: 0.8, // highest point of the series will be 70% away from the top
                    bottom: 0,
                },
            });

            const container = chartContainerRef.current;
            const toolTipWidth = 118;

            // Create and style the tooltip html element
            const toolTip = document.createElement('div');
            toolTip.style = `width: ${toolTipWidth}px; height: 280px; position: absolute; display: none; padding: 8px; box-sizing: border-box; font-size: 12px; text-align: left; z-index: 1000; top: 50px; left: 12px; pointer-events: none; border-radius: 4px 4px 0px 0px; border-bottom: none; box-shadow: 0 2px 5px 0 rgba(117, 134, 150, 0.45);font-family: -apple-system, BlinkMacSystemFont, 'Trebuchet MS', Roboto, Ubuntu, sans-serif; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;`;
            toolTip.style.background = `rgba(${'255, 235, 59'}, 0.58)`;
            toolTip.style.color = 'black';
            toolTip.style.borderColor = 'rgba( 239, 83, 80, 1)';
            container.appendChild(toolTip);
            chart.timeScale().fitContent()
            console.log('in data..')

            function updateData() {
                // if (ifDataLoadOk()) {
                //     return
                // }

                let dkey = (ACCOUNT_NAME + '_kline_tickdata').toLowerCase()
                Func.fetch.getObject("server.Data", "getDataByKey", [dkey], function (res) {
                    console.log('res..', res)
                    if (!res || ('data' in res == false)) {
                        console.log('account wait...')
                        return;
                    }

                    let data = res['data']
                    let stginfo = res['infos']['stginfo']
                
                    if ('data' in globalData == false) {
                        globalData['data'] = []
                    }
                    globalData['stginfo'] = stginfo
                    let startProfit = 0
                    data.forEach(item => {
                        let tmid = item['time']
                        if (TIMEIDS.indexOf(tmid) == -1) {
                            globalData['data'].push(item)
                            TIMEIDS.push(tmid)
                            // console.log('len timids', TIMEIDS.length)
                            candleSeries.update(item)

                            if ('extra' in item) {
                                let extra = item['extra']
                                let onlineprofit = parseFloat(extra['profit']) + parseFloat(res['infos']['unpayfee'])
                                profitSeries.update({ "time": item['time'], "value": onlineprofit })

                                let indikey = extra['name']
                                indiSeries.update({ "time": item['time'], "value": parseFloat(extra[indikey]) })
                                moneySeries.update({ "time": item['time'], "value": parseFloat(extra['maxusdt']) })
                                if ('tradeopt' in extra) {

                                    let tradeopt = extra['tradeopt']
                                    console.log('in tradeopt', extra, tradeopt)
                                    if (tradeopt == 'buy') {
                                        let mark = {
                                            time: item['time'],
                                            position: 'belowBar',
                                            color: '#2196F3',
                                            shape: 'arrowUp',
                                            text: 'Buy @',
                                        }

                                        allmarks.push(mark)

                                    } else if (tradeopt == 'sell') {
                                        let mark = {
                                            time: item['time'],
                                            position: 'aboveBar',
                                            color: '#e91e63',
                                            shape: 'arrowDown',
                                            text: 'Sell @',
                                        }

                                        allmarks.push(mark)
                                    } else if (tradeopt == 'cover_buy') {
                                        let mark = {
                                            time: item['time'],
                                            position: 'aboveBar',
                                            color: '#f68410',
                                            shape: 'circle',
                                            text: '平',
                                        }
                                        allmarks.push(mark)
                                    } else if (tradeopt == 'cover_sell') {
                                        let mark = {
                                            time: item['time'],
                                            position: 'aboveBar',
                                            color: '#f68410',
                                            shape: 'circle',
                                            text: '平',
                                        }
                                        allmarks.push(mark)
                                    }
                                }
                            }

                            let color = 'red'
                            if (item['opt'] == 'sell') {
                                color = 'green'
                            }

                            volumeSeries.update(
                                { time: item['time'], value: parseFloat(item['vol']), color: color }
                            )
                        }
                    })

                    console.log('len timids', TIMEIDS.length)

                    candleSeries.setMarkers(allmarks)

                    
                   


                    setloadstate(true)
                    setTitle('(' + stginfo['name'] + ')' + stginfo['variety'])
                    setTradedetails(res['infos']['tradedetails'])
                    setStockdetails(res['infos']['stockdetails'])


                    
                    if (TIMEIDS.length > maxLength) {
                        console.log('reset data')
                        
                        resetData()
                    }


                })
            }

            function resetData() {
                TIMEIDS = TIMEIDS.slice(TIMEIDS.length - startshowLength, TIMEIDS.length)
                globalData['data'] = globalData['data'].slice(TIMEIDS.length - startshowLength, TIMEIDS.length)
                candleSeries.setData([])
                profitSeries.setData([])
                volumeSeries.setData([])
                indiSeries.setData([])
                moneySeries.setData([])
                allmarks = []

                let data = globalData['data']
                data.forEach(item => {
                    let tmid = item['time']
                    candleSeries.update(item)
                    if ('extra' in item) {
                        let extra = item['extra']
                        let onlineprofit = parseFloat(extra['profit'])
                        profitSeries.update({ "time": item['time'], "value": onlineprofit })

                        let indikey = extra['name']
                        indiSeries.update({ "time": item['time'], "value": parseFloat(extra[indikey]) })
                        moneySeries.update({ "time": item['time'], "value": parseFloat(extra['maxusdt']) })
                        if ('tradeopt' in extra) {
                            let tradeopt = extra['tradeopt']
                            console.log('in tradeopt', extra, tradeopt)
                            if (tradeopt == 'buy') {
                                let mark = {
                                    time: item['time'],
                                    position: 'belowBar',
                                    color: '#2196F3',
                                    shape: 'arrowUp',
                                    text: 'Buy @',
                                }

                                allmarks.push(mark)

                            } else if (tradeopt == 'sell') {
                                let mark = {
                                    time: item['time'],
                                    position: 'aboveBar',
                                    color: '#e91e63',
                                    shape: 'arrowDown',
                                    text: 'Sell @',
                                }

                                allmarks.push(mark)
                            } else if (tradeopt == 'cover_buy') {
                                let mark = {
                                    time: item['time'],
                                    position: 'aboveBar',
                                    color: '#f68410',
                                    shape: 'circle',
                                    text: '平',
                                }
                                allmarks.push(mark)
                            } else if (tradeopt == 'cover_sell') {
                                let mark = {
                                    time: item['time'],
                                    position: 'aboveBar',
                                    color: '#f68410',
                                    shape: 'circle',
                                    text: '平',
                                }
                                allmarks.push(mark)
                            }
                        }
                    }

                    let color = 'red'
                    if (item['opt'] == 'sell') {
                        color = 'green'
                    }

                    volumeSeries.update(
                        { time: item['time'], value: parseFloat(item['vol']), color: color }
                    )
                })
                candleSeries.setMarkers(allmarks)

                chart.timeScale().applyOptions({ barSpacing: 1, minBarSpacing:0.001 })
                chart.timeScale().fitContent()
            }

            if (initok) {
                updateData()
            }

            console.log("this.props:", props)
            const interval = setInterval(function () {
                updateData()
            }, 2000);

            window.addEventListener('resize', handleResize)
            return () => {
                window.removeEventListener('resize', handleResize)
                clearInterval(interval)
                chart.remove()
                initok = true
            };
        }
        , []);

    return (
        <div style={{ paddingRight: "20px" }}>
            <h1>{loadok ? '' : '数据加载中...'}</h1>
            <h3 style={{ textAlign: "left" }}>{title}</h3>
            <div
                ref={chartContainerRef}
            />

            <h3>当前持仓</h3>
            <textarea style={{ height: 400, width: "100%" }} value={stockdetails} />

            <h3>平仓记录.csv</h3>
            <textarea style={{ height: 400, width: "100%" }} value={tradedetails} />
        </div>
    );
};

export default function Shipan(props) {
    return (
        <>
            <ChartComponent {...props}></ChartComponent>
        </>
    );
}