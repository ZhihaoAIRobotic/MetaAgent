import ForceGraph2D from 'react-force-graph-2d';
import React, { useEffect, useRef } from 'react';


const Wrapped2DGraph: React.FC = (props) => {

    const graphRef = useRef();

    useEffect(() => {
      if (graphRef.current) {
        // set d3Force
        const forceEngine = graphRef.current.d3Force('link')
        forceEngine.distance(80);
        forceEngine.strength(0.1);
        // const link: LinkObject = { source: 'Node 1', target: 'Node 2' };
        // graphRef.current.emitParticle(link);
      }
    }, []);
  
    return (
          <ForceGraph2D
            {...props}
            ref={graphRef}
          />
        ) 
  };


export default Wrapped2DGraph;