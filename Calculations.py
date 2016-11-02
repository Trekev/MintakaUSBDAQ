import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



def FPDifference(DF):
    DF['Difference'] = DF['Mintaka PA'] - DF['Mintaka PB']

def FPRMSD(DF):
    l = len(DF.index)
    rsmd = pd.DataFrame(DF['Difference'])
    rsmd['DiffSq']=rsmd['Difference']**2
    RSMD = np.sqrt((rsmd['DiffSq'].sum(axis=0))/(len(rsmd.index)))
    return RSMD

def OICDifference(DF, testAcol, testBcol, reference):
    DF['A - REF'] = testAcol - reference
    DF['B - REF'] = testBcol - reference

def OICRMSD(DF, testAVG, reference):
    
    rsmd = pd.DataFrame(testAVG - reference)
    rsmd['DiffSq']=rsmd**2
    RSMD = np.sqrt((rsmd['DiffSq'].sum(axis=0))/(len(rsmd.index)))
    return RSMD

def SE(df):
    SE = df.std()/np.sqrt(len(df))
    return SE

def MBE(df):
    MBEA = df['A - REF'].sum(axis=0)/len(df.index)
    MBEB = df['B - REF'].sum(axis=0)/len(df.index)
    return [MBEA, MBEB]


def statplot(df):
    df['Group'] = 0
    bins = np.array([870,900,930,960,990,1020])
    df['groups']=pd.cut(df['Paro P'], bins)
    
    plt2make = [['A - REF','Mintaka A Operational Inter-Comparison',r'$Test - Reference$']
                ,['B - REF','Mintaka B Operational Inter-Comparison',r'$Test - Reference$']
                ,['Difference','Functional Precision',r'$Test - Test$']]
    for i in plt2make:
        df.boxplot(column=i[0], by='groups')

        plt.title(i[1], fontsize=14, fontweight='bold')
        plt.ylim([-1.5,1.5])
        plt.xlabel('Pressure (mb)')
        plt.ylabel('Pressure Difference (mb)')
        plt.text(4, 1.0, i[2])
        plt.axhspan(-0.1, 0.1, color='r', alpha=0.25)
        plt.show()

            
