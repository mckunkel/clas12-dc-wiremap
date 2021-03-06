import sys
from os import path
import numpy as np

from .dc_tables import (CalibrationDCHVCrate,
    CalibrationDCHVSupplyBoard, CalibrationDCHVSubslot,
    CalibrationDCHVDoublet, CalibrationDCHVDoubletPin,
    CalibrationDCHVDoubletPinMap, CalibrationDCHVTranslationBoard,
    CalibrationDCWire, CalibrationDCSignalTranslationBoard,
    CalibrationDCSignalCable, CalibrationDCSignalReadoutConnector,
    initialize_session)

from . import ccdb_goetz as ccdb
from .dc_fill_tables import dc_fill_tables
from .cached_property import cached_property

Crate            = CalibrationDCHVCrate
SupplyBoard      = CalibrationDCHVSupplyBoard
Subslot          = CalibrationDCHVSubslot
Doublet          = CalibrationDCHVDoublet
DoubletPin       = CalibrationDCHVDoubletPin
DoubletPinMap    = CalibrationDCHVDoubletPinMap
TransBoard       = CalibrationDCHVTranslationBoard
Wire             = CalibrationDCWire
SignalCable      = CalibrationDCSignalCable
ReadoutConnector = CalibrationDCSignalReadoutConnector

ccdb.rc.connstr = 'mysql://clas12reader@clasdb.jlab.org/clas12'

class DCWires(object):
    _tables = [Crate            ,
               SupplyBoard      ,
               Subslot          ,
               Doublet          ,
               #DoubletPin       ,
               #DoubletPinMap    ,
               TransBoard       ,
               Wire             ,
               #SignalCable      ,
               #ReadoutConnector ,
    ]

    def __init__(self):
        self.run = 0
        self.variation = 'default'

    runnum = 1
    @cached_property
    def session(self):
        return initialize_session()

    @property
    def run(self):
        return self._run

    @run.setter
    def run(self,run):
        run = int(run)
        assert run >= 0
        self._run = run

    def clear(self):
        attrs = '''\
            session
            crate_id
            slot_id
            supply_board_id
            subslot_id
            quad_id
        '''.split()
        for attr in attrs:
            try:
                delattr(self,attr)
            except:
                pass

    def fetch_data(self):
        self.clear()
        for Table in DCWires._tables:
            name = Table.__tablename__
            print('fetching table:',name)
            data = ccdb.get_table(name,
                run=self.run,
                variation=self.variation)
            for d in data:
                rowdata = {n:np.asscalar(v) for n,v in zip(data.dtype.names, d)}
                row = Table(**rowdata)
                self.session.add(row)
            del data
        self.session.flush()

    def query_column(self,column):
        q = self.session.query(
            Wire.sector,Wire.superlayer,Wire.layer,Wire.wire,
            column)\
        .join(Subslot,Doublet,TransBoard,SupplyBoard,Crate)\
        .filter(
            SupplyBoard.wire_type == 'sense',
            Wire.wire >= TransBoard.wire_offset,
            Wire.wire <  TransBoard.wire_offset + TransBoard.nwires)\
        .order_by(
            Wire.sector,
            Wire.superlayer,
            Wire.layer,
            Wire.wire)
        arr = np.array(q.all()).T[4]
        return arr.reshape((6,6,6,112))

    @cached_property
    def crate_id(self):
        return self.query_column(Crate.id)

    @cached_property
    def slot_id(self):
        return self.query_column(SupplyBoard.slot_id)

    @cached_property
    def supply_board_id(self):
        return self.query_column(SupplyBoard.id)

    @cached_property
    def subslot_id(self):
        return self.query_column(Subslot.subslot_id)

    @cached_property
    def subslot_channel_id(self):
        return self.query_column(Doublet.channel_id)

    @cached_property
    def distr_box_type(self):
        return self.query_column(Doublet.distr_box_type)

    @cached_property
    def quad_id(self):
        return self.query_column(Doublet.quad_id)

    @cached_property
    def doublet_id(self):
        return self.query_column(Doublet.doublet_id)

    @cached_property
    def trans_board_id(self):
        return self.query_column(TransBoard.board_id)

    @cached_property
    def trans_board_slot_id(self):
        return self.query_column(TransBoard.slot_id)

    @cached_property
    def doublet_pin_map_doublet_id(self):
        q = self.session.query(Wire.sector,Wire.superlayer,Wire.layer,Wire.wire,
               DoubletPin.doublet_id)\
        .join(Subslot,Doublet,TransBoard, SupplyBoard,DoubletPin,DoubletPinMap)\
        .filter(
            SupplyBoard.wire_type == 'sense',
            Wire.wire >= TransBoard.wire_offset,
            Wire.wire <  TransBoard.wire_offset + TransBoard.nwires)\
        .order_by(
            Wire.sector,
            Wire.superlayer,
            Wire.layer,
            Wire.wire)

        doublet_pin_map = np.array(q.all()).T[4]
        return doublet_pin_map.reshape((6,6,6,112))

    @cached_property
    def doublet_pin_map_pin_id(self):
        q = self.session.query(Wire.sector,Wire.superlayer,Wire.layer,Wire.wire,
               DoubletPin.pin_id)\
        .join(Subslot,Doublet,TransBoard, SupplyBoard,DoubletPin,DoubletPinMap)\
        .filter(
            SupplyBoard.wire_type == 'sense',
            Wire.wire >= TransBoard.wire_offset,
            Wire.wire <  TransBoard.wire_offset + TransBoard.nwires)\
        .order_by(
            Wire.sector,
            Wire.superlayer,
            Wire.layer,
            Wire.wire)

        doublet_pin_map = np.array(q.all()).T[4]
        return doublet_pin_map.reshape((6,6,6,112))

    @cached_property
    def doublet_pin_map_layer(self):
        q = self.session.query(Wire.sector,Wire.superlayer,Wire.layer,Wire.wire,
               DoubletPin.layer)\
        .join(Subslot,Doublet,TransBoard, SupplyBoard,DoubletPin,DoubletPinMap)\
        .filter(
            SupplyBoard.wire_type == 'sense',
            Wire.wire >= TransBoard.wire_offset,
            Wire.wire <  TransBoard.wire_offset + TransBoard.nwires)\
        .order_by(
            Wire.sector,
            Wire.superlayer,
            Wire.layer,
            Wire.wire)

        doublet_pin_map = np.array(q.all()).T[4]
        return doublet_pin_map.reshape((6,6,6,112))

    @cached_property
    def doublet_pin_doublet_id(self):
        q = self.session.query(Wire.sector,Wire.superlayer,Wire.layer,Wire.wire,
               DoubletPin.doublet_id)\
        .join(Subslot,Doublet,TransBoard, SupplyBoard)\
        .filter(
            SupplyBoard.wire_type == 'sense',
            Wire.wire >= TransBoard.wire_offset,
            Wire.wire <  TransBoard.wire_offset + TransBoard.nwires)\
        .order_by(
            Wire.sector,
            Wire.superlayer,
            Wire.layer,
            Wire.wire)

        doublet_pin = np.array(q.all()).T[4]
        return doublet_pin.reshape((6,6,6,112))

    @cached_property
    def doublet_pin_pin_id(self):
        q = self.session.query(Wire.sector,Wire.superlayer,Wire.layer,Wire.wire,
               DoubletPin.pin_id)\
        .join(Subslot,Doublet,TransBoard, SupplyBoard)\
        .filter(
            SupplyBoard.wire_type == 'sense',
            Wire.wire >= TransBoard.wire_offset,
            Wire.wire <  TransBoard.wire_offset + TransBoard.nwires)\
        .order_by(
            Wire.sector,
            Wire.superlayer,
            Wire.layer,
            Wire.wire)

        doublet_pin = np.array(q.all()).T[4]
        return doublet_pin.reshape((6,6,6,112))


    @cached_property
    def signal_cable_id(self):
        q = self.session.query(Wire.sector,Wire.superlayer,Wire.layer,Wire.wire,
               SignalCable.id)\
        .join(Subslot,Doublet,TransBoard, SupplyBoard)\
        .filter(
            SupplyBoard.wire_type == 'sense',
            Wire.wire >= TransBoard.wire_offset,
            Wire.wire <  TransBoard.wire_offset + TransBoard.nwires)\
        .order_by(
            Wire.sector,
            Wire.superlayer,
            Wire.layer,
            Wire.wire)

        signal_cable = np.array(q.all()).T[4]
        return signal_cable.reshape((6,6,6,112))

    @cached_property
    def readout_connector_id(self):
        q = self.session.query(Wire.sector,Wire.superlayer,Wire.layer,Wire.wire,
               ReadoutConnector.id)\
        .join(Subslot,Doublet,TransBoard, SupplyBoard)\
        .filter(
            SupplyBoard.wire_type == 'sense',
            Wire.wire >= TransBoard.wire_offset,
            Wire.wire <  TransBoard.wire_offset + TransBoard.nwires)\
        .order_by(
            Wire.sector,
            Wire.superlayer,
            Wire.layer,
            Wire.wire)

        readout_connector = np.array(q.all()).T[4]
        return readout_connector.reshape((6,6,6,112))




if __name__ == '__main__':
    from matplotlib import pyplot, cm
    from clas12_wiremap import plot_wiremap

    dcwm = DCWires()
    dcwm.fetch_data()

    fig = pyplot.figure()
    fig.canvas.set_window_title('Crate Wire Connections')
    ax = fig.add_subplot(1,1,1)
    pt,(cb,cax) = plot_wiremap(ax,dcwm.crate_id + 1)
    cax.set_ylabel('Crate ID')

    fig = pyplot.figure()
    fig.canvas.set_window_title('Supply Board Wire Connections')
    ax = fig.add_subplot(1,1,1)
    res = plot_wiremap(ax,dcwm.supply_board_id + 1)
    pt,cbax = res
    cb,cax = cbax
    cax.set_ylabel('Supply Board ID')

    fig = pyplot.figure()
    fig.canvas.set_window_title('Subslot Wire Connections')
    ax = fig.add_subplot(1,1,1)
    pt,(cb,cax) = plot_wiremap(ax,dcwm.subslot_id + 1)
    cax.set_ylabel('Subslot ID')

    fig = pyplot.figure()
    fig.canvas.set_window_title('Subslot and Crate Wire Connections')
    ax = fig.add_subplot(1,1,1)
    pt,(cb,cax) = plot_wiremap(ax,(dcwm.subslot_id+1) + 10*(dcwm.crate_id+1))
    cax.set_ylabel(r'Subslot ID + 10 $\times$ Crate ID')

    pyplot.show()

