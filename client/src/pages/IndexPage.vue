<template>
  <q-page class="row justify-evenly">
    <q-stepper v-model="step" :vertical="phone" color="primary" animated class="fit" flat>
      <q-step :name="1" prefix="1" title="File Upload" icon="settings" :done="step > 1">
        <q-uploader :url="api.defaults.baseURL + '/upload'" @uploaded="uploaded" ref="uploader" accept=".pdf" max-files="1" auto-upload />

        <q-option-group class="q-mt-lg" v-model="engine" :options="engines" color="primary" />

        <q-stepper-navigation>
          <q-btn
            @click="extractInfo"
            color="primary"
            :loading="extracting"
            :disable="!storename"
            style="width: 150px"
            rounded
          >
            Extract info
            <template v-slot:loading>
              <q-spinner-hourglass class="on-left" />
              Extracting ...
            </template>
          </q-btn>
        </q-stepper-navigation>
      </q-step>

      <q-step
        :name="2"
        prefix="2"
        title="Information Validation"
        icon="create_new_folder"
        :done="step > 2"
      >
        <div class="row">
          <!--<div class="col">
            .col
          </div>-->
          <div class="col">
            <q-scroll-area style="height: 500px; width: 1390px">
              <x-spreadsheet-wrapper ref="spreadsheet" />
            </q-scroll-area>
          </div>
        </div>

        <q-stepper-navigation>
          <q-btn @click="goToStep3" color="primary" label="Validate" rounded />
          <!--<q-btn flat @click="step = 1" color="primary" label="Back" class="q-ml-sm" />-->
        </q-stepper-navigation>
      </q-step>

      <q-step :name="3" prefix="3" title="Data Export" icon="assignment">
        <q-option-group class="q-mt-lg" v-model="target" :options="targets" color="primary" />

        <q-stepper-navigation>
          <q-btn @click="download" color="primary" label="Download" rounded />
          <q-btn @click="goToStep2" color="primary" label="Back" class="q-ml-sm" rounded flat />
        </q-stepper-navigation>
      </q-step>
    </q-stepper>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { api } from 'boot/axios'
import { useQuasar } from 'quasar'
import XSpreadsheetWrapper from 'components/XSpreadsheetWrapper.vue'
import * as XLSX from 'xlsx'

const $q = useQuasar()
const step = ref(1)
const data = ref()
const engine = ref('textract')
const target = ref('csv')
const workbook = ref()
const uploader = ref()
const storename = ref(false)
const extracting = ref(false)
const spreadsheet = ref()
const engines = [
  {
    label: 'Textract',
    value: 'textract',
  },
  {
    label: 'EasyOCR',
    value: 'easyocr',
  },
]
const targets = [
  {
    label: 'CSV',
    value: 'csv',
  },
  {
    label: 'XLSX',
    value: 'xlsx',
  },
]
const phone = $q.platform.is.mobile

/**
 * Extracts information from the uploaded file if it exists and the upload was successful.
 *
 * This function checks if there is a file uploaded and if the upload was successful (status 200).
 * If so, it logs the file name, sets the extracting state to true, and sends a POST request to the '/extract' endpoint
 * with the filename, storename, and engine as payload.
 *
 * On a successful response, it updates the data with the response data, navigates to the next step, and sets the extracting state to false.
 * If the request fails, it catches the error but does not handle it.
 */
function extractInfo() {
  if (
    uploader.value.files[0] &&
    uploader.value.files[0].xhr &&
    uploader.value.files[0].xhr.status === 200
  ) {
    console.log(`Extracting info from ${uploader.value.files[0].name}`)
    extracting.value = true
    api
      .post('/extract', {
        filename: uploader.value.files[0].name,
        storename: storename.value,
        engine: engine.value,
      })
      .then((response) => {
        if (response && response.data && response.data.error) {
          $q.notify({
            progress: true,
            color: 'negative',
            position: 'bottom',
            message: response.data.error,
            icon: 'report_problem'
          })
          extracting.value = false
        } else {
          data.value = response.data
          goToStep2()
          extracting.value = false
        }
      })
      .catch((error) => {
        console.log(error)
        $q.notify({
          progress: true,
          color: 'negative',
          position: 'bottom',
          message: 'Error extracting information',
          icon: 'report_problem'
        })
        extracting.value = false
      })
  }
}

/**
 * Navigates to step 2 and processes the spreadsheet data.
 *
 * This function sets the current step to 2 and then, after a delay of 100 milliseconds,
 * it reads the workbook data, converts it to a format suitable for the spreadsheet component,
 * loads the data into the spreadsheet, and adjusts the column widths to fit the content.
 *
 * @function goToStep2
 */
function goToStep2() {
  step.value = 2
  setTimeout(() => {
    const wb = workbook.value || XLSX.read(data.value, { type: 'string' })
    const dt = spreadsheet.value.workbookToData(wb)
    spreadsheet.value.loadData(dt)
    spreadsheet.value.autofitColumnWidths()
  }, 100)
}

/**
 * Navigates to step 3 in the process and converts the spreadsheet data to a workbook.
 *
 * This function performs the following actions:
 * 1. Sets the current step to 3.
 * 2. Converts the data from the spreadsheet into a workbook and assigns it to the workbook variable.
 */
function goToStep3() {
  step.value = 3
  workbook.value = spreadsheet.value.dataToWorkbook()
}

/**
 * Downloads the current workbook as a file.
 *
 * The filename is derived from the `storename` value, excluding the file extension.
 * The file is saved with the extension specified by the `target` value.
 *
 * @function download
 */
function download() {
  const filename = storename.value.split('.')[0]
  XLSX.writeFile(workbook.value, `${filename}.${target.value}`)
}

/**
 * Handles the uploaded file information.
 *
 * @param {Object} info - The information about the uploaded file.
 * @param {XMLHttpRequest} info.xhr - The XMLHttpRequest object associated with the upload.
 * @param {number} info.xhr.status - The HTTP status code of the upload response.
 * @param {string} info.xhr.responseText - The response text of the upload.
 */
function uploaded(info) {
  if (info.xhr && info.xhr.status === 200) {
    storename.value = info.xhr.responseText
  }
}
</script>
