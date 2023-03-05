import dipsl
from .DIP_Node import Node
from .DIP_Parser import Parser

class SourceNode(Node):
    keyword: str = 'source'

    @staticmethod
    def is_node(parser):
        parser.kwd_source()
        if parser.is_parsed('kwd_source'):
            parser.part_comment()
            return SourceNode(parser)
            
    def parse(self, env):
        parser = Parser(
            code=self.value_raw,
            line=self.line,
            source=self.source
        )
        # import a remote source
        parser.part_reference()
        if parser.is_parsed('part_reference'):
            sources = env.request(parser.value_ref, namespace="sources")
            for key, val in sources.items():
                if key in env.sources:
                    raise Exception("Reference source alread exists:", parser.name)
                env.sources[key] = val
        else:
            # inject value of a node
            parser.part_name(path=False) # parse name
            parser.part_equal()          # parse equal sign
            parser.part_value()          # parse value
            if parser.value_ref:
                self.inject_value(env, parser)
            if parser.name not in env.sources:
                if parser.value_raw.endswith('dip'):
                    p = dipsl.DIP()
                    p.load(parser.value_raw)
                    p.parse()
                    env.sources[parser.name] = p
                else:
                    with open(parser.value_raw,'r') as f:
                        env.sources[parser.name] = f.read()
            else:
                raise Exception("Reference source alread exists:", parser.name)
        return None
