# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Networks
                                 A QGIS plugin
 Networks
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-02-26
        copyright            : (C) 2018 by Patrick Palmier
        email                : patrick.palmier@cerema.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Patrick Palmier'
__date__ = '2018-02-26'
__copyright__ = '(C) 2018 by Patrick Palmier'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import *
from qgis.utils import *
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterString,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterField,
                       QgsProcessingParameterExpression,
                       QgsProcessingParameterFileDestination)
import io

class FichierAff(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    INPUT = 'INPUT'
    IJ='IJ'
    TYPE='TYPE'
    VOLAU='VOLAU'
    LIGNE='LIGNE'
    PAR_LIGNE='PAR_LIGNE'
    FICHIER_AFF='FICHIER_AFF'
    ENCODAGE='ENCODAGE'
    


    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        nom_ij="i+'-'+j"
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Network'),
                [QgsProcessing.TypeVectorLine]
            )
        )
        

        self.addParameter(
            QgsProcessingParameterExpression(
                self.IJ,
                self.tr('ij'),
                parentLayerParameterName=self.INPUT,
                defaultValue=nom_ij
               
                
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.LIGNE,
                self.tr('Line'),
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.String,
                optional=True
            )
        )
        
        self.addParameter(
            QgsProcessingParameterString(
                self.VOLAU,
                self.tr('Flows'),
                "volau"
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.TYPE,
                self.tr('Link type'),
                defaultValue='type'
                
            )
        )


        self.addParameter(
            QgsProcessingParameterFile(
                self.FICHIER_AFF,
                self.tr('aff output file'),
                QgsProcessingParameterFile.File,
                "TXT"
                
                
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.ENCODAGE,
                self.tr('Encoding'),
                "utf_8_sig"
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Flows layer')
                
            )
        )
        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        arcs= self.parameterAsSource(parameters, self.INPUT, context)
        ij_exp=QgsExpression(self.parameterAsExpression(parameters,self.IJ,context))
        ligne=self.parameterAsFields(parameters,self.LIGNE,context)
        volume=self.parameterAsString(parameters,self.VOLAU,context)
        type_arc=self.parameterAsString(parameters,self.TYPE,context)
        fichier_aff=self.parameterAsFile(parameters,self.FICHIER_AFF,context)
        encodage=self.parameterAsString(parameters,self.ENCODAGE,context)
        
        links=arcs
        champs={}
        fij={}
        trafic={}
        if len(ligne)==0:
            champs2=QgsFields()
            champs2.append(QgsField("i",QVariant.String,len=15))
            champs2.append(QgsField("j",QVariant.String,len=15))
            champs2.append(QgsField("ij",QVariant.String,len=35))
            champs2.append(QgsField("volume",QVariant.Double))
            champs2.append(QgsField("type",QVariant.String,len=35))
        else:
            champs2=QgsFields()
            champs2.append(QgsField("i",QVariant.String,len=15))
            champs2.append(QgsField("j",QVariant.String,len=15))
            champs2.append(QgsField("ij",QVariant.String,len=35))
            champs2.append(QgsField("ligne",QVariant.String,len=35))
            champs2.append(QgsField("volume",QVariant.Double))
            champs2.append(QgsField("decalage",QVariant.Double))
            champs2.append(QgsField("type",QVariant.String,len=35))


        (iti,affectation) = self.parameterAsSink(parameters, self.OUTPUT,context,champs2,QgsWkbTypes.MultiLineString, arcs.sourceCrs())

        
        aff=io.open(fichier_aff,"r",encoding=encodage)

        ijContexte=self.createExpressionContext(parameters,context, links)
        ij_exp.prepare(ijContexte)

        
        
        valeurs=links.getFeatures()
        for i,j in enumerate(valeurs):
            ijContexte.setFeature(j)
            ij=ij_exp.evaluate(ijContexte)
            fij[ij]=j
            
        for k,i in enumerate(aff):
            elements=i.split(";")
            
            if k==0:

                for ide, e in enumerate(elements):
                    champs[e.strip("\"").strip("\n").strip("\r")]=ide

            else:
                if len(ligne)==0:
                    cle=tuple([elements[champs['i']],elements[champs['j']]])
                else:
                    cle=tuple([elements[champs['i']],elements[champs['j']],elements[champs[ligne[0]]].strip("\"")])

                volau=elements[champs[volume]].replace(",",".")
                type2=elements[champs[type_arc]]

                if cle not in trafic:
                    trafic[cle]=(0,'0')
                trafic[cle]=(trafic[cle][0]+float(volau),type2)    


        for i in trafic:
            cle_ij= i[0]+"-"+i[1]
            if cle_ij in fij:
                f=QgsFeature()
                f.setGeometry(fij[cle_ij].geometry())
                
                if len(ligne)==0:
                    f.setAttributes([i[0],i[1],cle_ij,trafic[i][0],trafic[i][1]])
                else:
                    f.setAttributes([i[0],i[1],cle_ij,i[2],trafic[i][0],0.0,trafic[i][1]])
                iti.addFeature(f)
        aff.close()        
        
        del champs2
        del trafic
        del fij

        return {self.OUTPUT: affectation}


    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'get_link_flows_data'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Get link flows data')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Analysis')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Analysis'

    def tr(self, string):
        return QCoreApplication.translate('FichierAff', string)
        
    def shortHelpString(self):
        return self.tr("""
        Generate a linear objects layer with the links used in assignment (with a volume of passengers>0) in particular to produce flows maps.
		
        Parameters:
            network: the network links layer 
			ij: an expression do describe the link id ("id" attribute or expression)
            line (optonal): the line id. If line id is filled the layer will have as many superposed links as they have identical links but with a different transit line id (You should used "shift lines' alg to view flows maps in this case
			link type: the type of link
            aff ouput file: Choose a network corresponding <FILENAME>_aff.txt output file
            enconding: text encoding
            flows layer: name of the flows layer generated
            
            
            
        """)

    def createInstance(self):
        return FichierAff()