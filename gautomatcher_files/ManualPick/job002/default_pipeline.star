
data_pipeline_general

_rlnPipeLineJobCounter                       3
 

data_pipeline_processes

loop_ 
_rlnPipeLineProcessName #1 
_rlnPipeLineProcessAlias #2 
_rlnPipeLineProcessType #3 
_rlnPipeLineProcessStatus #4 
Import/job001/       None            0            2 
ManualPick/job002/       None            3            0 
 

data_pipeline_nodes

loop_ 
_rlnPipeLineNodeName #1 
_rlnPipeLineNodeType #2 
Import/job001/micrographs.star            1 
ManualPick/job002/coords_suffix_manualpick.star            2 
ManualPick/job002/micrographs_selected.star            1 
 

data_pipeline_input_edges

loop_ 
_rlnPipeLineEdgeFromNode #1 
_rlnPipeLineEdgeProcess #2 
Import/job001/micrographs.star ManualPick/job002/ 
 

data_pipeline_output_edges

loop_ 
_rlnPipeLineEdgeProcess #1 
_rlnPipeLineEdgeToNode #2 
Import/job001/ Import/job001/micrographs.star 
ManualPick/job002/ ManualPick/job002/coords_suffix_manualpick.star 
ManualPick/job002/ ManualPick/job002/micrographs_selected.star 
 
