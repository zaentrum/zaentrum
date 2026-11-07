// The design system's components in the states chino's target uses, rendered by the
// real package (v0.4.0) so the drawing kit can copy their exact markup.
import React, { useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import {
  Button, IconButton, Select, Field, Input, Textarea, Switch, Checkbox, ActionMenu, MultiSelect,
  FilterBar, FilterTabs, Tabs, Modal, Banner, toast, Toaster, EmptyState, Spinner, Status, Badge,
  Heading, Text, Kbd, Divider, Toolbar, Tooltip, Card, Chevron, Lockup, Tile, TileGroup,
} from '@nalet/design-system';
import { Play, Plus, Trash2, Check, Download, ListPlus, Bell, Search, Settings, LogOut, User, Pencil, Eye, Film, Library, Wrench, Users } from 'lucide-react';

const Ex = ({ id, children, w }) => (
  <section data-ex={id} style={{ padding: 16, borderBottom: '1px solid #1F2633', width: w }}>
    <p style={{ font: '12px monospace', color: '#7B8597', margin: '0 0 8px' }}>{id}</p>
    <div className="ex-body">{children}</div>
  </section>
);
const noop = () => {};
const langs = [{ value: 'orig', label: 'Original' }, { value: 'en', label: 'English' }, { value: 'de', label: 'German' }];

function App() {
  useEffect(() => {
    toast('Added to watchlist', { state: 'success' });
    toast("Couldn't add it to the list. Can't reach the server.", { state: 'error' });
  }, []);
  return (
    <div>
      <Ex id="button-variants">
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <Button variant="primary" leading={<Play size={16} />}>play</Button>
          <Button variant="default" leading={<Plus size={16} />}>add to list</Button>
          <Button variant="ghost">cancel</Button>
          <Button variant="danger">delete account</Button>
          <Button variant="primary" loading>connect</Button>
          <Button variant="default" disabled>disabled</Button>
        </div>
      </Ex>
      <Ex id="button-sizes">
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <Button size="sm">small</Button><Button size="md">medium</Button><Button size="lg" variant="primary" leading={<Play size={18} />}>large</Button>
        </div>
      </Ex>
      <Ex id="iconbutton">
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <IconButton label="search"><Search size={18} /></IconButton>
          <IconButton label="watched" variant="default"><Check size={18} /></IconButton>
          <IconButton label="notifications" variant="ghost"><Bell size={18} /></IconButton>
          <IconButton label="play" variant="primary"><Play size={18} /></IconButton>
          <IconButton label="delete" variant="danger"><Trash2 size={18} /></IconButton>
          <IconButton label="small" size="sm"><Pencil size={14} /></IconButton>
          <IconButton label="large" size="lg"><Play size={20} /></IconButton>
        </div>
      </Ex>
      <Ex id="select" w={360}><Select options={langs} defaultValue="orig" aria-label="audio" /></Ex>
      <Ex id="select-sizes" w={360}><div style={{ display: 'grid', gap: 8 }}><Select selectSize="sm" options={langs} aria-label="s" /><Select selectSize="lg" options={langs} aria-label="l" /><Select options={langs} disabled aria-label="d" /><Select options={langs} invalid aria-label="i" /></div></Ex>
      <Ex id="field-select" w={420}>
        <Field label="Audio" hint="Titles play with audio in the language you pick here, where they have it.">
          <Select options={langs} defaultValue="orig" />
        </Field>
      </Ex>
      <Ex id="field-input" w={420}>
        <Field label="Name" hint="Up to 40 characters." required><Input defaultValue="Sunday films" /></Field>
      </Ex>
      <Ex id="field-input-error" w={420}>
        <Field label="Server address" error="No server answers at this address."><Input defaultValue="media.example" /></Field>
      </Ex>
      <Ex id="textarea" w={420}><Field label="What happened?"><Textarea defaultValue="The picture froze after the intro." rows={3} /></Field></Ex>
      <Ex id="switch" w={420}>
        <div style={{ display: 'grid', gap: 12 }}>
          <Switch label="Auto-skip intros and recaps" defaultChecked />
          <Switch label="Download over Wi-Fi only" />
          <Switch label="small" size="sm" defaultChecked />
        </div>
      </Ex>
      <Ex id="checkbox" w={420}><div style={{ display: 'grid', gap: 8 }}><Checkbox label="Watchlist" defaultChecked /><Checkbox label="Sunday films" /></div></Ex>
      <Ex id="actionmenu" w={420}>
        <ActionMenu label="more for Sprite Fright" items={[
          { id: 'play', label: 'play', icon: <Play size={16} />, onSelect: noop },
          { id: 'watched', label: 'mark as watched', icon: <Check size={16} />, onSelect: noop },
          { id: 'list', label: 'add to list', icon: <ListPlus size={16} />, onSelect: noop },
          { id: 'remove', label: 'remove from continue watching', icon: <Trash2 size={16} />, danger: true, onSelect: noop },
        ]} />
      </Ex>
      <Ex id="actionmenu-labelled" w={420}>
        <ActionMenu label="sort" buttonLabel="newest first" items={[
          { id: 'new', label: 'newest first', onSelect: noop }, { id: 'az', label: 'a to z', onSelect: noop },
          { id: 'rating', label: 'best rated', onSelect: noop }, { id: 'added', label: 'recently added', onSelect: noop },
        ]} />
      </Ex>
      <Ex id="multiselect" w={420}>
        <MultiSelect label="genres" value={['animation']} onChange={noop} options={[
          { value: 'animation', label: 'animation', count: 12 }, { value: 'comedy', label: 'comedy', count: 7 },
          { value: 'drama', label: 'drama', count: 9 }, { value: 'science fiction', label: 'science fiction', count: 5 },
        ]} />
      </Ex>
      <Ex id="filterbar" w={1100}>
        <FilterBar
          search={{ value: '', onChange: noop, placeholder: 'filter movies…', label: 'filter movies' }}
          filters={[
            { type: 'multiselect', id: 'genre', label: 'genres', value: ['animation'], onChange: noop, options: [{ value: 'animation', label: 'animation', count: 12 }, { value: 'comedy', label: 'comedy', count: 7 }] },
            { type: 'select', id: 'decade', label: 'decade', value: '', onChange: noop, emptyValue: '', options: [{ value: '', label: 'all' }, { value: '2020', label: '2020s' }, { value: '2010', label: '2010s' }, { value: 'old', label: 'before 1980' }] },
            { type: 'select', id: 'sort', label: 'sort', value: 'new', onChange: noop, options: [{ value: 'new', label: 'newest first' }, { value: 'az', label: 'a to z' }] },
          ]}
          onClearAll={noop}
          resultCount="12 movies"
        />
      </Ex>
      <Ex id="filtertabs" w={600}>
        <FilterTabs label="notifications" value="all" onChange={noop} tabs={[{ id: 'all', label: 'all', count: 7 }, { id: 'unread', label: 'unread', count: 2, state: 'information' }]} />
      </Ex>
      <Ex id="tabs" w={600}>
        <Tabs defaultValue="s1" items={[{ value: 's1', label: 'season 1' }, { value: 's2', label: 'season 2' }, { value: 'sp', label: 'specials' }]} />
      </Ex>
      <Ex id="banner" w={720}>
        <div style={{ display: 'grid', gap: 8 }}>
          <Banner state="information">Can't reach the server. Your downloads still play.</Banner>
          <Banner state="warning" actions={<Button size="sm">try again</Button>} onDismiss={noop}>Couldn't refresh. The list shows what was loaded.</Banner>
          <Banner state="error" details="503 Service Unavailable">Couldn't delete the list. The server ran into a problem.</Banner>
          <Banner state="success" onDismiss={noop}>The report reached the people who run this server.</Banner>
        </div>
      </Ex>
      <Ex id="emptystate" w={600}>
        <EmptyState illustration="empty" title="nothing in this list yet" description="Add a title from its page, with add to list." actions={<Button variant="default">browse movies</Button>} />
      </Ex>
      <Ex id="emptystate-search" w={600}><EmptyState illustration="search" title="no matches" description="Nothing in the library matches “zz”." size="sm" /></Ex>
      <Ex id="emptystate-error" w={600}><EmptyState illustration="error" title="couldn't load the library" description="The server ran into a problem." actions={<Button>try again</Button>} /></Ex>
      <Ex id="emptystate-done" w={600}><EmptyState illustration="done" title="all caught up" size="sm" /></Ex>
      <Ex id="emptystate-unknown" w={600}><EmptyState illustration="unknown" title="this title isn't in the library any more" size="sm" /></Ex>
      <Ex id="banner-details-open" w={720}><Banner state="error" details="503 Service Unavailable" defaultDetailsOpen>Couldn't delete the list. The server ran into a problem.</Banner></Ex>
      <Ex id="card-header" w={420}><Card header="language" headerAside={<Button size="sm">reset</Button>}><Text>Audio and subtitles.</Text></Card></Ex>
      <Ex id="divider-variants" w={400}><div style={{ display: 'grid', gap: 12 }}><Divider heavy /><Divider label="or" /></div></Ex>
      <Ex id="input-disabled" w={400}><Input disabled defaultValue="media.example.com" /></Ex>
      <Ex id="filterbar-collapsed" w={360}>
        <FilterBar collapseBelow={2000}
          search={{ value: '', onChange: noop, placeholder: 'search movies', label: 'search movies' }}
          filters={[
            { type: 'multiselect', id: 'genre', label: 'genres', value: ['animation'], onChange: noop, options: [{ value: 'animation', label: 'animation', count: 12 }] },
            { type: 'select', id: 'decade', label: 'decade', value: '', onChange: noop, emptyValue: '', options: [{ value: '', label: 'all' }, { value: '2020', label: '2020s' }] },
          ]}
          onClearAll={noop} resultCount="9 of 10" />
      </Ex>
      <Ex id="multiselect-none" w={360}><MultiSelect label="genres" value={[]} onChange={noop} options={[{ value: 'animation', label: 'animation', count: 12 }]} /></Ex>
      <Ex id="tilegroup" w={1100}>
        <TileGroup legend="apps" description="what you can open">
          <Tile title="chino" description="Movies and shows" icon={Film} href="#" status="online" />
          <Tile title="catalog" description="Browse the catalog" icon={Library} href="#" badge="3" badgeTone="warning" />
          <Tile title="catalog management" description="Scan and settings" icon={Wrench} href="#" status="degraded" />
          <Tile title="people" description="Accounts and invites" icon={Users} href="#" disabled />
        </TileGroup>
      </Ex>
      <Ex id="tile-sizes" w={1100}><div style={{ display: 'flex', gap: 12 }}><Tile title="small" icon={Film} href="#" size="sm" /><Tile title="large" description="A large tile" icon={Film} href="#" size="lg" /><Tile title="kpi" variant="kpi" value="1,240" unit="titles" delta={{ value: '+12', direction: 'up', tone: 'positive' }} /></div></Ex>
      <Ex id="spinner"><div style={{ display: 'flex', gap: 16 }}><Spinner label="loading" /><Spinner size={32} label="loading" /></div></Ex>
      <Ex id="status" w={720}>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <Status state="success" text="downloaded" /><Status state="information" text="downloading · 40%" /><Status state="warning" text="check needed" />
          <Status state="error" text="couldn't download" /><Status state="neutral" text="waiting" /><Status state="success" text="downloaded" appearance="text" />
        </div>
      </Ex>
      <Ex id="badge"><div style={{ display: 'flex', gap: 8 }}><Badge>movie</Badge><Badge tone="blue">2</Badge><Badge tone="green">new</Badge><Badge tone="amber">expires in 3 days</Badge><Badge dot tone="blue">unread</Badge></div></Ex>
      <Ex id="type" w={720}>
        <Heading level={1}>Sprite Fright</Heading><Heading level={2}>continue watching</Heading><Heading level={3}>season 1</Heading>
        <Text>Teenagers on a trip into the woods meet the small folk who live there.</Text>
        <Text tone="muted" size="sm">2021 · 10 min · comedy</Text>
      </Ex>
      <Ex id="kbd"><span>press <Kbd>OK</Kbd> to play, <Kbd>back</Kbd> to close</span></Ex>
      <Ex id="divider" w={400}><Divider /></Ex>
      <Ex id="toolbar" w={720}><Toolbar label="downloads"><Button size="sm" leading={<Trash2 size={14} />}>delete</Button><Button size="sm" variant="ghost">select all</Button></Toolbar></Ex>
      <Ex id="card" w={420}><Card><Heading level={3}>language</Heading><Text size="sm">Audio and subtitles.</Text></Card></Ex>
      <Ex id="lockup"><div style={{ display: 'flex', gap: 24, alignItems: 'center' }}><Chevron /><Lockup /></div></Ex>
      <Ex id="tooltip"><Tooltip content="mark as watched"><IconButton label="watched"><Check size={18} /></IconButton></Tooltip></Ex>
      <Modal open onClose={noop} title="create list" footer={<><Button variant="ghost">cancel</Button><Button variant="primary">create list</Button></>}>
        <Field label="Name"><Input defaultValue="Sunday films" /></Field>
      </Modal>
      <Toaster />
    </div>
  );
}
createRoot(document.getElementById('root')).render(<App />);
