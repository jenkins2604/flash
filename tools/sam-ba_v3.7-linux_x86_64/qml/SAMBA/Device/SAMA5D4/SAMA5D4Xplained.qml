/*
 * Copyright (c) 2015-2016, Atmel Corporation.
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms and conditions of the GNU General Public License,
 * version 2, as published by the Free Software Foundation.
 *
 * This program is distributed in the hope it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
 * more details.
 */

import QtQuick 2.3
import SAMBA.Device.SAMA5D4 3.7

/*!
	\qmltype SAMA5D4Xplained
	\inqmlmodule SAMBA.Device.SAMA5D4
	\brief Contains a specialization of the SAMA5D4 QML type for the
	       SAMA5D4 Xplained Ultra board.
*/
SAMA5D4 {
	name: "sama5d4-xplained"

	aliases: [ "sama5d4-xult" ]

	description: "SAMA5D4 Xplained Ultra"

	config {
		serial {
			instance: 6 /* USART3 */
			ioset: 1
		}

		// MT47H128M16
		extram {
			preset: 2
		}

		sdmmc {
			instance: 1
			ioset: 1
			partition: 0
			busWidth: 0
			voltages: 4 /* 3.3V */
		}

		serialflash {
			instance: 0
			ioset: 1
			chipSelect: 0
			freq: 48
		}

		nandflash {
			ioset: 1
			busWidth: 8
			header: 0xc1e04e07
		}
	}
}
