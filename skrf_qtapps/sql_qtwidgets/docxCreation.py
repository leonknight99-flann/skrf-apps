import os
import docx
import tempfile

import pyodbc

from skrf import Network

from docx.enum.text import WD_BREAK

from copy import deepcopy

import numpy as np
import matplotlib.pyplot as plt

from datetime import date

file_types = ('.csv', '.s1p', '.s2p', '.s3p', '.s4p')
testDataPath = '\\\\Filesrv\\Test\\RFData\\'

plt.rcParams["font.family"] = "Calibri"

def create_docx_report(instrument_dictionary, revision_number='1', selected_file_only=[]):

    date_now = date.today().strftime("%d/%m/%Y")

    for partID in instrument_dictionary:

        # Get Part ID Information
        mydb = pyodbc.connect("DRIVER={SQL Server};SERVER=SQLSRV22;DATABASE=ISM;UID=FLUser;PWD=MelonBall", readonly=True)
        mydb_cursor = mydb.cursor()
        partid_sql_info = mydb_cursor.execute("select Instrument_Number, Instrument_ID, Part_ID, Series, Var_Suffix, var_id, SeriesName from vw_Instrument_VarDetails where (Part_ID = ?)",(partID)).fetchone()
        mydb.close()

        instrument_number = partid_sql_info.Instrument_Number
        instrument_id = str(partid_sql_info.Instrument_ID)
        var_suffix = partid_sql_info.Var_Suffix
        seriesName = partid_sql_info.SeriesName

        if var_suffix is None:
            var_suffix = ''

        model = f"{instrument_number} {var_suffix}"
        
        for sn in instrument_dictionary[partID]:
            # Open Template
            doc = docx.Document(os.path.abspath(os.path.join(os.path.dirname(__file__), "report_template.docx")))

            # Table Data
            table = doc.tables[0]

            paragraph = table.cell(0, 0).add_paragraph()
            run = paragraph.add_run(sn)
            run.font.size = docx.shared.Pt(9)
            run.font.name = 'Calibri'
            run.italic = False

            paragraph = table.cell(0, 1).add_paragraph()
            run = paragraph.add_run(model)
            run.font.size = docx.shared.Pt(9)
            run.font.name = 'Calibri'
            run.italic = False

            paragraph = table.cell(0, 2).add_paragraph()
            run = paragraph.add_run(partID)
            run.font.size = docx.shared.Pt(9)
            run.font.name = 'Calibri'
            run.italic = False

            paragraph = table.cell(0, 3).add_paragraph()
            run = paragraph.add_run(seriesName)
            run.font.size = docx.shared.Pt(9)
            run.font.name = 'Calibri'
            run.italic = False

            paragraph = table.cell(1, 2).add_paragraph()
            run = paragraph.add_run(date_now)
            run.font.size = docx.shared.Pt(9)
            run.font.name = 'Calibri'
            run.italic = False

            paragraph = table.cell(1, 3).add_paragraph()
            run = paragraph.add_run(instrument_id)
            run.font.size = docx.shared.Pt(9)
            run.font.name = 'Calibri'
            run.italic = False

            paragraph = table.cell(1, 4).add_paragraph()
            run = paragraph.add_run(revision_number)
            run.font.size = docx.shared.Pt(9)
            run.font.name = 'Calibri'
            run.italic = False

            # Add Plots
            try:
                list_files = os.listdir(testDataPath+partID)
                list_files = [name for name in list_files if name.lower().endswith(file_types)]
                list_files = [name for name in list_files if sn in name]
                # list_files = list(filter(lambda f: not any(s in f.lower() for s in ['top_of_band', 'bottom_of_band']), list_files))

                if selected_file_only:
                    list_files = [f for f in list_files if f in selected_file_only]

                for file in list_files:
                    # Duplicating table for each file after the first
                    if list_files.index(file) != 0:
                        orig_table = doc.tables[0]

                        tbl_element = deepcopy(orig_table._element)
                        new_table = doc.add_table(rows=1, cols=1)  # Temporary table to get a reference
                        new_table._element.addnext(tbl_element)

                        doc.add_paragraph()  # Add a paragraph break after the table
                    
                    if file.lower().endswith('.csv'):
                        '''Original CSV Format'''
                        if list_files.index(file) == 0:
                            # Get Analyser and Tester from CSV
                            parameters = np.loadtxt(testDataPath+partID+'\\'+file, delimiter=',', usecols=2, dtype=str)
                            analyser = parameters[2][8:]
                            tester = parameters[0][2:]

                            paragraph = table.cell(1, 0).add_paragraph()
                            run = paragraph.add_run(analyser)
                            run.font.size = docx.shared.Pt(9)
                            run.font.name = 'Calibri'
                            run.italic = False

                            paragraph = table.cell(1, 1).add_paragraph()
                            run = paragraph.add_run(tester)
                            run.font.size = docx.shared.Pt(9)
                            run.font.name = 'Calibri'
                            run.italic = False

                        data = np.loadtxt(testDataPath+partID+'\\'+file, delimiter=',', usecols=(0, 1, 3))
                        freq = data[:, 0] 
                        mag_s_param = data[:, 1]
                        tested_specification = data[:, 2]

                        title = file[:-4].replace('_', ' ')
                        
                        fig, ax = plt.subplots(figsize=(8, 10))
                        
                        ax.plot(freq, mag_s_param)
                        ax.plot(freq, tested_specification, '--', label='Specification', color='#004124')
                        ax.set_xlabel('Frequency (GHz)')
                        ax.set_ylabel('Magnitude (dB)')
                        ax.grid(True, which='both')
                        ax.minorticks_on()
                        ax.grid(which='minor', linewidth=0.5, alpha=0.5)
                        ax.set_ylim(top=0, bottom=min(min(mag_s_param), 2*min(tested_specification)))
                        ax.set_title(title)
                        fig.tight_layout()

                        tempdir = tempfile.gettempdir()
                        img_path = os.path.join(tempdir, f"test_data_print_temp.png")
                        plt.savefig(img_path)
                        plt.close()
                        paragraph = doc.add_paragraph()
                        run = paragraph.add_run()
                        run.add_picture(img_path, width=docx.shared.Inches(6))
                        paragraph.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
                        os.remove(img_path)
                    
                    elif file.lower().endswith(('.s1p', '.s2p', '.s3p', '.s4p')):
                        '''SNP Format'''
                        ntwk = Network(testDataPath+partID+'\\'+file)
                        fig = ntwk.plot_s_db(m=0, x='freq', show_legend=False)
                        plt.title(f"{file}")

                        tempdir = tempfile.gettempdir()
                        img_path = os.path.join(tempdir, f"test_data_print_temp.png")
                        plt.savefig(img_path)
                        plt.close()

                        doc.add_picture(img_path, width=docx.shared.Inches(6))
                        
                        os.remove(img_path)

                    if list_files.index(file) != len(list_files)-1:
                        doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
            except:
                print(f"Could not find directory for PartID: {partID}")
                continue

            doc.save(f"{sn}_test_report_R{revision_number}.docx")#{testDataPath+partID+'\\'

# create_docx_report({'F01999': ['278751'], 'F06416': ['323379']})