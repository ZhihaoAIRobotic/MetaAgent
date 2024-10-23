"use client";

import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { Layout, Button } from 'antd';
import { HomeOutlined } from '@ant-design/icons';
import Link from 'next/link';
import SpriteText from 'three-spritetext';
import { Switch } from "@/components/ui/switch"
import { NodeObject } from 'react-force-graph-2d';
import Sidebar from '@/components/sheetsidebar';
// import ForceGraph2D from 'react-force-graph-2d';

const { Header, Content } = Layout;
const ForceGraph3D = dynamic(() => import('react-force-graph-3d'), { ssr: false });
const Wrapped2DGraph = dynamic(() => import('@/components/wrap2dgraph'), { ssr: false });


interface WindowSize {
  width: number | undefined;
  height: number | undefined;
}

const useWindowSize = () => {
  const [windowSize, setWindowSize] = useState<WindowSize>({
    width: undefined,
    height: undefined,
  });

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', handleResize);
    handleResize();
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowSize;
};

const Graph: React.FC = () => {
  const windowSize = useWindowSize();
  const [itemContent, setItemContent] = useState(['', '']);
  const [is2DEnabled, setIs2DEnabled] = useState(false);
  // const graphRef = useRef();
  const [data, setData] = useState({
    nodes: [
      { id: 'Node 1' },
      { id: 'Node 2' },
      { id: 'Node 3' }
    ],
    links: [
      { source: 'Node 1', target: 'Node 2' },
      { source: 'Node 2', target: 'Node 3' },
      { source: 'Node 3', target: 'Node 1' }
    ]
  });

  useEffect(() => {
    fetch('http://localhost:5000/get-json')
      .then(res => res.json())
      .then(dataJson => setData(dataJson))
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  const clickNode = (node: NodeObject) => {
    console.log(node.id);
    const links = data.links.filter(l => l.source === node || l.target === node);
    const linkDescriptions = links.map(l => l.description).join("\n");
    const nodeDescription = node.description;
    setItemContent([nodeDescription, linkDescriptions]);
  };

  const commonProps = {
    graphData: data,
    nodeColor: () => '#2d2e2e',
    nodeOpacity: 0.99,
    linkColor: () => 'rgba(199,199,199,0.89)',
    linkWidth: () => 1,
    backgroundColor: '#f2f2f2',
    onNodeClick: clickNode,
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header className={'shadow-2xl'} style={{ background: '#2d2e2e', padding: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '36px', zIndex: 10 }}>
        <Link href="/">
          <Button icon={<HomeOutlined />} style={{ margin: '12px', zIndex: 3, height: '28px', background: '#2d2e2e', color: 'white' }}>
            
          </Button>
        </Link>
      </Header>
      <Content style={{ position: 'relative', height: 'calc(100vh - 64px)', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 }}>
          {is2DEnabled ? (
            <Wrapped2DGraph
              {...commonProps}
              nodeResolution={18}
              nodeCanvasObject={(node, ctx, globalScale) => {
                const label = (node.id as string).replace(/"/g, "");
                const fontSize = 6;
                ctx.font = `${fontSize}px Arial Black`;
                ctx.fillStyle = 'rgba(139,139,139,0.99)';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(label, node.x!, node.y! + 9);
              }}
              nodeCanvasObjectMode={() => 'before'}
            />
          ) : (
            <ForceGraph3D
              {...commonProps}
              nodeResolution={8}
              linkOpacity={0.99}
              nodeThreeObject={(node: NodeObject) => {
                const textWithoutQuote = (node.id as string).replace(/"/g, "");
                const sprite = new SpriteText(textWithoutQuote);
                sprite.color = 'rgba(139,139,139,0.99)';
                sprite.textHeight = 2;
                sprite.backgroundColor = 'rgba(110,110,0,0)';
                sprite.padding = 1;
                sprite.borderRadius = 1;
                sprite.position.y = -8;
                sprite.fontFace = 'Arial Black';
                return sprite;
              }}
              nodeThreeObjectExtend={true}
            />
          )}
        </div>
        
        <div style={{ position: 'absolute', top: '16px', left: '16px', zIndex: 10 }}>
          <div className="bg-white p-2 rounded-md shadow-md flex items-center space-x-2">
            <span className="text-sm font-medium">2D Graph</span>
            <Switch
              checked={is2DEnabled}
              onCheckedChange={setIs2DEnabled}
            />
          </div>
        </div>

        <Sidebar item_content={itemContent} />
      </Content>
    </Layout>
  );
};

export default Graph;