import itertools
from pathlib import Path
from typing import List


class SplittedFile:
    @staticmethod
    def split(filepath : Path, part_size : int, delete_original = False):
        """
        splits a file to the parts
        
        raises:
            Exception
            FileNotFoundError
        """
        if part_size == 0:
            raise Exception(f'part_size == 0')
        
        if filepath.exists():
            filesize = filepath.stat().st_size
            
            n_parts = filesize // part_size
            
            if filesize - part_size*n_parts != 0:
                n_parts += 1
            
            if n_parts > 100:
                raise Exception('n_parts > 100')
                   
            b = filepath.read_bytes()
            for n in range(n_parts):
                part_filepath = filepath.parent / (filepath.name + f'.part{n}')
                part_filepath.write_bytes(b[n*part_size:(n+1)*part_size])
            
            
            if delete_original:
                filepath.unlink()
        else:
            raise FileNotFoundError()
        
    
    @staticmethod
    def merge(filepath : Path, delete_parts = False):
        """
        if filepath does not exist, merges parts of file if they exist
        
        example
        
        filename.ext.part0
        filename.ext.part1
        ...
        merged to filename.ext
        """
        
        parts : List[Path] = []
        for n in itertools.count(start=0):
            part_filepath = filepath.parent / (filepath.name + f'.part{n}')
            if part_filepath.exists():
                parts.append(part_filepath)
            else:
                break
        
        if len(parts) != 0:
            if not filepath.exists():
                bytes_parts = []
                for part_filepath in parts:
                    bytes_parts.append( part_filepath.read_bytes() )
                
                b = b''.join(bytes_parts)
                
                filepath.write_bytes(b)
            
            if delete_parts:
                for part_filepath in parts:
                    part_filepath.unlink()
