"use client";

import React, { useState, useEffect } from 'react';
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import {  
  Accordion,  
  AccordionContent,  
  AccordionItem,  
  AccordionTrigger,  
} from "@/components/ui/accordion";  
import { Button } from "@/components/ui/button";
import { Waypoints, Orbit, ChevronRight, ChevronLeft, Info } from "lucide-react";


type ItemType = string[];

const Sidebar = ({item_content}: {item_content: ItemType}) => {
  const [collapsed, setCollapsed] = useState(false);
  const [contentType, setContentType] = useState('upload');

  const toggleCollapse = () => {
    setCollapsed(!collapsed);
  };

  const items = [  
    {  
      icon: <Info size={24}  />,
      title: "Node Description",  
      content: item_content[0]  
    },  
    {  
      icon: <Waypoints size={24} />,
      title: "Relationships",  
      content: item_content[1]
    }
  ];  

  const SidebarContent = () => {
    if (collapsed) {
      return (
        <div className="flex flex-col items-center space-y-4 mt-4">
          {items.map((item, index) => (
            <Button key={index} variant="ghost" size="icon" className="w-12 h-12">
              {item.icon}
            </Button>
          ))}
        </div>
      );
    }

    return (
      <Sheet>
        <Accordion type="multiple" className="w-full" defaultValue={['item-0', 'item-1']} style={{ marginTop: '-1rem' }}>  
        <div className="accordion-content-container">
        {items.map((item, index) => (  
          <AccordionItem key={index} value={`item-${index}`} className="-mt-4">  
            <AccordionTrigger >  
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                {item.icon}
              </div>
              <div className="ml-2 text-lg font-bold">
                {item.title}
              </div>
            </div>
            </AccordionTrigger> 
            <div >
            <AccordionContent >  
              <div className='text-lg'>
               {item.content.split('\n').map((line: string, index: string) => (
                   <span key={index}>
                     {line.replace(/"/g, "")}
                     <br />
                   </span>
                   ))}  
              </div>
            </AccordionContent>  
          </div> 
          </AccordionItem>  
        ))}  
        </div>
      </Accordion>  
      </Sheet>
    );
  };

  // Change content type when item_content changes
  useEffect(() => {
    console.log(item_content);
    if (JSON.stringify(item_content)!==JSON.stringify(['',''])){
      setContentType('orbit');
    }
  }, [item_content]);


  return (
    <div 
      style={{ zIndex: 1 }}
      className={`absolute top-0 right-0 flex flex-col bg-gray-100 dark:bg-gray-800 transition-all duration-300 shadow-2xl ${
        collapsed ? 'w-16' : 'w-96'
      } h-full`}
      >
        {/* Control Buttons for Desktop */}
        <div className={`flex ${collapsed ? 'justify-center' : 'justify-between'} p-4`}>
          {!collapsed && (
            <div>
              {/* <Button variant="outline" size="icon" onClick={() => setContentType('upload')} className={contentType === 'upload' ? 'bg-gray-700 text-white' : ''}>
                <Upload size={24} />
              </Button> */}
              <Button variant="outline" size="icon" onClick={() => setContentType('orbit')} className={contentType === 'orbit' ? 'bg-gray-700 text-white' : ''} >
                <Orbit size={24} />
              </Button>
            </div>
          )}
          <Button variant="outline" size="icon" onClick={toggleCollapse} >
            {collapsed ? <ChevronLeft size={24} /> : <ChevronRight size={24} />}
          </Button>
        </div>
        <div className="flex-grow p-4 overflow-auto">
          <SidebarContent />
        </div>
      </div>
  );
};

export default Sidebar;
