"""Clair3 plugin for tb-profiler variant calling"""

__version__ = '0.1.0'
from .cli import get_downloaded_models, __clair3_model_path__
from pathogenprofiler import run_cmd, Vcf, TempFolder
import shutil


from pathogenprofiler.variant_calling import VariantCaller

class Clair3(VariantCaller):
    __software__ = "clair3"
    __cli_params__ = [
        {
            'args':['--clair3_model'], 
            'kwargs':{
                'type': str, 
                'help': 'Path to Clair3 model',
                'choices': get_downloaded_models(),
            }
        }
    ]
    
    def call_variants(self):
        if self.clair3_model is None:
            raise ValueError("Please provide a Clair3 model with `--clair3_model`")
        with TempFolder() as tmp_dir:
            self.tmp_dir = tmp_dir
            self.clair3_model_path = f'{__clair3_model_path__}/{self.clair3_model}'
            if self.platform=="nanopore":
                if self.bed_file:
                    self.vcf_file = "%s.vcf.gz" % (self.prefix)
                    self.calling_cmd = "%(clair3_path)s -b %(bam_file)s -f %(ref_file)s --bed_fn=%(bed_file)s --threads %(threads)s --output %(tmp_dir)s --platform ont --model_path %(clair3_model_path)s --include_all_ctgs --no_phasing_for_fa --haploid_sensitive --sample_name=%(bam_sample_name)s --chunk_size=20000 -t %(threads)s" % vars(self)
                else:
                    self.vcf_file = "%s.short_variants.vcf.gz" % (self.prefix)
                    self.calling_cmd = "%(clair3_path)s -b %(bam_file)s -f %(ref_file)s --threads %(threads)s --output %(tmp_dir)s --platform ont --model_path %(clair3_model_path)s --include_all_ctgs --no_phasing_for_fa --haploid_sensitive --sample_name=%(bam_sample_name)s --chunk_size=20000 -t %(threads)s" % vars(self)
            else:
                raise NotImplementedError("%s not implemented for %s platform" % (self.__software__,self.platform))
            
            run_cmd(self.calling_cmd)
            shutil.move(f"{tmp_dir}/merge_output.vcf.gz", self.vcf_file)

        return Vcf(self.vcf_file)
    
