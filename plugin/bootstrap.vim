let s:cache_dir = exists('$XDG_CACHE_HOME') ? $XDG_CACHE_HOME : $HOME . '/.cache'
let s:default_venvs = s:cache_dir . '/chromatin/venvs'
let s:venvs = get(g:, 'chromatin_venv_dir', s:default_venvs)
let s:venv = s:venvs . '/chromatin'
let s:script = fnamemodify(expand('<sfile>'), ':p:h:h') . '/scripts/bootstrap.py'
let s:req = get(g:, 'chromatin_pip_req', 'chromatin')
let s:py_exe = 'python3'

function! ChromatinJobStderr(id, data, event) abort "{{{
  echoerr 'error in chromatin rpc job on channel ' . a:id . ': ' . string(a:data)
endfunction "}}}

function! BootstrapChromatin() abort "{{{
  try
    call jobstart([s:py_exe, s:script, s:venv, s:req], { 'rpc': v:true, 'on_stderr': 'ChromatinJobStderr' })
  catch //
    echo v:exception
  endtry
endfunction "}}}

command! BootstrapChromatin call BootstrapChromatin()

if get(g:, 'chromatin_autobootstrap', 1)
  BootstrapChromatin
endif
