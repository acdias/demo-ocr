<template>
  <q-card>
    <div ref="spreadsheetContainer" style="height: 100%"></div>
  </q-card>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import 'x-data-spreadsheet/dist/xspreadsheet.css'
import Spreadsheet from 'x-data-spreadsheet'
import * as XLSX from 'xlsx'

// Define a ref for the spreadsheet container
const spreadsheetContainer = ref(null)
let spreadsheet = ref(null)

// Initialize the spreadsheet on mounted
onMounted(() => {
  if (spreadsheetContainer.value) {
    spreadsheet.value = new Spreadsheet(spreadsheetContainer.value, {
      showToolbar: true, // Optionally hide the toolbar
      showGrid: true,
    })
    spreadsheet.value.sheet.selector.hide()
  }
})

// Cleanup when the component is destroyed
onBeforeUnmount(() => {
  if (spreadsheet.value) {
    //spreadsheet.destroy()
    console.log('Spreadsheet destroyed', spreadsheet)
  }
})

/**
 * Change the column width based on content
 *
 * @returns {Arraybuffer} An x-spreadsheet data
 */
function autofitColumnWidths() {
  const widths = getColumnWidthsByText()
  for (let i = 0; i < widths.length; i++) {
    spreadsheet.value.sheet.data.setColWidth(i, widths[i] + 10)
  }
  return spreadsheet.value.reRender()
}

/**
 * Calculates the widths of columns based on the text content of the cells.
 * Iterates through the rows and cells of the spreadsheet data to determine
 * the maximum width required for each column.
 *
 * @returns {number[]} An array of column widths where each index corresponds
 *                     to the maximum width of the column at that index.
 */
function getColumnWidthsByText() {
  const widths = []
  const data = spreadsheet.value.getData()
  for (let i = 0; i < Object.keys(data[0].rows).length - 1; i++) {
    for (let j = 0; j < Object.keys(data[0].rows[i].cells).length; j++) {
      const cell = data[0].rows[i].cells[j]
      if (cell && cell.text) {
        const width = getStringWidth(cell.text)
        if (!widths[j] || width > widths[j]) {
          widths[j] = width
        }
      }
    }
  }
  return widths
}

/**
 * Calculates the width of a given text string using a specified font.
 *
 * @param {string} text - The text string to measure.
 * @param {string} [font='13px Arial'] - The font style to use for measurement (default is '13px Arial').
 * @returns {number} - The width of the text string in pixels.
 */
function getStringWidth(text, font = '13px Arial') {
  // Create a temporary canvas element
  const canvas = document.createElement('canvas')
  const context = canvas.getContext('2d')
  // Set the font style
  context.font = font
  // Measure the width of the text
  const width = context.measureText(text).width
  return width
}

/**
 * Converts a workbook object to x-spreadsheet data.
 *
 * @param {Object} xlsxObject - The XLSX workbook object.
 *
 * @returns {ArrayBuffer} An x-spreadsheet data.
 */
function workbookToData(workbook) {
  return stox(workbook)
}

/**
 * Converts x-spreadsheet data to XLSX workbook object
 *
 * @param {Object} data - The x-spreadsheet data object
 *
 * @returns {xlsxObject} A XLSX workbook object
 */
 function dataToWorkbook(data = spreadsheet.value.getData()) {
  return xtos(data)
}

/**
 * Converts data from SheetJS to x-spreadsheet
 *
 * @param  {Object} wb SheetJS workbook object
 *
 * @returns {Object[]} An x-spreadsheet data
 */
function stox(wb) {
  var out = []
  wb.SheetNames.forEach(function (name) {
    var o = { name: name, rows: {} }
    var ws = wb.Sheets[name]
    if (!ws || !ws['!ref']) return
    var range = XLSX.utils.decode_range(ws['!ref'])
    // sheet_to_json will lost empty row and col at begin as default
    range.s = { r: 0, c: 0 }
    var aoa = XLSX.utils.sheet_to_json(ws, {
      raw: false,
      header: 1,
      range: range,
    })

    aoa.forEach(function (r, i) {
      var cells = {}
      r.forEach(function (c, j) {
        cells[j] = { text: c }

        var cellRef = XLSX.utils.encode_cell({ r: i, c: j })

        if (ws[cellRef] != null && ws[cellRef].f != null) {
          cells[j].text = '=' + ws[cellRef].f
        }
      })
      o.rows[i] = { cells: cells }
    })

    o.merges = []
    ;(ws['!merges'] || []).forEach(function (merge, i) {
      //Needed to support merged cells with empty content
      if (o.rows[merge.s.r] == null) {
        o.rows[merge.s.r] = { cells: {} }
      }
      if (o.rows[merge.s.r].cells[merge.s.c] == null) {
        o.rows[merge.s.r].cells[merge.s.c] = {}
      }

      o.rows[merge.s.r].cells[merge.s.c].merge = [merge.e.r - merge.s.r, merge.e.c - merge.s.c]

      o.merges[i] = XLSX.utils.encode_range(merge)
    })

    out.push(o)
  })

  return out
}

/**
 * Converts data from x-spreadsheet to SheetJS
 *
 * @param  {Object[]} sdata An x-spreadsheet data object
 *
 * @returns {Object} A SheetJS workbook object
 */
function xtos(sdata) {
  var out = XLSX.utils.book_new()
  sdata.forEach(function (xws) {
    var ws = {}
    var rowobj = xws.rows
    var minCoord = { r: 0, c: 0 },
      maxCoord = { r: 0, c: 0 }
    for (var ri = 0; ri < rowobj.len; ++ri) {
      var row = rowobj[ri]
      if (!row) continue

      Object.keys(row.cells).forEach(function (k) {
        var idx = +k
        if (isNaN(idx)) return

        var lastRef = XLSX.utils.encode_cell({ r: ri, c: idx })
        if (ri > maxCoord.r) maxCoord.r = ri
        if (idx > maxCoord.c) maxCoord.c = idx

        var cellText = row.cells[k].text,
          type = 's'
        if (!cellText) {
          cellText = ''
          type = 'z'
        } else if (!isNaN(Number(cellText))) {
          cellText = Number(cellText)
          type = 'n'
        } else if (cellText.toLowerCase() === 'true' || cellText.toLowerCase() === 'false') {
          cellText = Boolean(cellText)
          type = 'b'
        }

        ws[lastRef] = { v: cellText, t: type }

        if (type == 's' && cellText[0] == '=') {
          ws[lastRef].f = cellText.slice(1)
        }

        if (row.cells[k].merge != null) {
          if (ws['!merges'] == null) ws['!merges'] = []

          ws['!merges'].push({
            s: { r: ri, c: idx },
            e: {
              r: ri + row.cells[k].merge[0],
              c: idx + row.cells[k].merge[1],
            },
          })
        }
      })
    }
    ws['!ref'] = minCoord
      ? XLSX.utils.encode_range({
          s: minCoord,
          e: maxCoord,
        })
      : 'A1'

    XLSX.utils.book_append_sheet(out, ws, xws.name)
  })

  return out
}

defineExpose({
  instance: spreadsheet,
  loadData: (data) => spreadsheet.value.loadData(data),
  autofitColumnWidths,
  workbookToData,
  dataToWorkbook,
})
</script>

<style scoped>
/* Ensure the container is styled to have a defined height and width */
div {
  width: 100%;
  height: 400px; /* Adjust as needed */
}
</style>
